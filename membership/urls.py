from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    path('select/', views.membership_select, name='select'),
    path('checkout/', views.create_checkout_session, name='create_checkout'),
    path('portal/', views.customer_portal, name='portal'),
    path('success/', views.success, name='success'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]