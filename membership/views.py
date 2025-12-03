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
    # Get customer data to show "Next Bill Date" if it exists
    try:
        customer = request.user.stripe_customer
    except:
        customer = None

    return render(request, 'membership/select.html', {
        'publishable_key': settings.STRIPE_PUBLIC_KEY,
        'customer': customer
    })


@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            # 1. Get or Create Stripe Customer
            customer, created = StripeCustomer.objects.get_or_create(user=request.user)

            if not customer.stripe_customer_id:
                stripe_cust = stripe.Customer.create(
                    email=request.user.email,
                    metadata={'user_id': request.user.id}
                )
                customer.stripe_customer_id = stripe_cust.id
                customer.save()

            # 2. Determine Mode (Subscription vs One-Time)
            data = json.loads(request.body)
            price_id = data.get('price_id')
            custom_amount = data.get('custom_amount')

            line_items = []
            mode = 'subscription'  # Default

            if price_id:
                # SUBSCRIPTION (Tiers)
                line_items.append({'price': price_id, 'quantity': 1})
                mode = 'subscription'

            elif custom_amount:
                # ONE-TIME DONATION (Fixed)
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': '480pDreams Donation'},
                        'unit_amount': int(custom_amount),
                    },
                    'quantity': 1,
                })
                mode = 'payment'  # <--- Changed from 'subscription'

            # 3. Create Session
            checkout_session = stripe.checkout.Session.create(
                customer=customer.stripe_customer_id,
                payment_method_types=['card'],
                line_items=line_items,
                mode=mode,
                success_url='https://www.480pdreams.com/membership/success/',
                cancel_url='https://www.480pdreams.com/membership/select/',
            )
            return HttpResponse(json.dumps({'sessionId': checkout_session.id}), content_type="application/json")

        except Exception as e:
            return HttpResponse(json.dumps({'error': str(e)}), status=400)


@login_required
def customer_portal(request):
    try:
        customer = request.user.stripe_customer
        session = stripe.billing_portal.Session.create(
            customer=customer.stripe_customer_id,
            return_url='https://www.480pdreams.com/membership/select/'
        )
        return redirect(session.url)
    except:
        return redirect('membership:select')


def success(request):
    return render(request, 'membership/success.html')


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Only activate membership if it was a SUBSCRIPTION mode
        if session.get('mode') == 'subscription':
            handle_checkout_session(session)

    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_update(event['data']['object'])

    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])

    return HttpResponse(status=200)


# Helpers
def handle_checkout_session(session):
    stripe_id = session['customer']
    try:
        customer = StripeCustomer.objects.get(stripe_customer_id=stripe_id)
        customer.stripe_subscription_id = session.get('subscription')
        customer.status = 'active'
        customer.save()
        customer.user.profile.is_patron = True
        customer.user.profile.save()
    except StripeCustomer.DoesNotExist:
        pass


def handle_subscription_update(sub):
    try:
        customer = StripeCustomer.objects.get(stripe_customer_id=sub['customer'])
        customer.status = sub['status']
        # Note: We could sync 'current_period_end' here if we parsed the timestamp
        customer.save()
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