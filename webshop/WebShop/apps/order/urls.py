from django.conf.urls import *
from WebShop.apps.order.views import CheckoutView, OrderSuccessView, ConfirmAddressView


urlpatterns = patterns('',
    # Shopping Cart
    url(r'checkout/address$', ConfirmAddressView.as_view(), name="confirm-address-route"),
    url(r'checkout/payment$', CheckoutView.as_view(), name="checkout-route"),
    url(r'success/$', OrderSuccessView.as_view(), name="order-success-route")
)