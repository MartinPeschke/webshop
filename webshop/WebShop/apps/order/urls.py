from django.conf.urls import *
from WebShop.apps.order.views import CheckoutView, OrderSuccessView


urlpatterns = patterns('',
    # Shopping Cart
    url(r'checkout/$', CheckoutView.as_view(), name="checkout-route"),
    url(r'success/$', OrderSuccessView.as_view(), name="order-success-route")
)