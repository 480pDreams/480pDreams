import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import StripeCustomer
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def membership_select(request):
    return render(request, 'membership/select.html', {
        'publishable_key': settings.STRIPE_PUBLIC_KEY
    })


@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            # 1. Get or Create Stripe Customer
            customer, created = StripeCustomer.objects.get_or_create(user=request.user)

            # If they don't have a stripe ID yet, create one in Stripe
            if not customer.stripe_customer_id:
                stripe_cust = stripe.Customer.create(
                    email=request.user.email,
                    metadata={'user_id': request.user.id}
                )
                customer.stripe_customer_id = stripe_cust.id
                customer.save()

            # 2. Determine Price
            # (We will send 'price_id' or 'amount' from the frontend form)
            data = json.loads(request.body)
            price_id = data.get('price_id')
            custom_amount = data.get('custom_amount')  # e.g. 500 for $5.00

            line_items = []
            if price_id:
                # Standard Tier
                line_items.append({'price': price_id, 'quantity': 1})
            elif custom_amount:
                # Custom Donation Logic
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': '480pDreams Membership (Custom)'},
                        'unit_amount': int(custom_amount),  # Must be in cents!
                        'recurring': {'interval': 'month'},
                    },
                    'quantity': 1,
                })

            # 3. Create Session
            checkout_session = stripe.checkout.Session.create(
                customer=customer.stripe_customer_id,
                payment_method_types=['card'],
                line_items=line_items,
                mode='subscription',
                success_url='https://www.480pdreams.com/membership/success/',
                cancel_url='https://www.480pdreams.com/membership/select/',
            )
            return HttpResponse(json.dumps({'sessionId': checkout_session.id}), content_type="application/json")

        except Exception as e:
            return HttpResponse(json.dumps({'error': str(e)}), status=400)


@login_required
def customer_portal(request):
    # Send user to Stripe to manage billing
    customer = request.user.stripe_customer
    session = stripe.billing_portal.Session.create(
        customer=customer.stripe_customer_id,
        return_url='https://www.480pdreams.com/profile/'
    )
    return redirect(session.url)


def success(request):
    return render(request, 'membership/success.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Activate the user
        handle_checkout_session(session)

    elif event['type'] == 'customer.subscription.updated':
        sub = event['data']['object']
        handle_subscription_update(sub)

    elif event['type'] == 'customer.subscription.deleted':
        sub = event['data']['object']
        handle_subscription_deleted(sub)

    return HttpResponse(status=200)


# Helper Functions
def handle_checkout_session(session):
    stripe_id = session['customer']
    # Find user and mark active
    try:
        customer = StripeCustomer.objects.get(stripe_customer_id=stripe_id)
        customer.stripe_subscription_id = session['subscription']
        customer.status = 'active'
        customer.save()

        # Also update the Legacy flag for compatibility
        customer.user.profile.is_patron = True
        customer.user.profile.save()
    except StripeCustomer.DoesNotExist:
        pass


def handle_subscription_update(sub):
    try:
        customer = StripeCustomer.objects.get(stripe_customer_id=sub['customer'])
        customer.status = sub['status']  # active, past_due, etc
        customer.save()

        # Sync legacy flag
        is_active = (sub['status'] == 'active' or sub['status'] == 'trialing')
        customer.user.profile.is_patron = is_active
        customer.user.profile.save()
    except:
        pass


def handle_subscription_deleted(sub):
    try:
        customer = StripeCustomer.objects.get(stripe_customer_id=sub['customer'])
        customer.status = 'canceled'
        customer.save()
        customer.user.profile.is_patron = False
        customer.user.profile.save()
    except:
        pass