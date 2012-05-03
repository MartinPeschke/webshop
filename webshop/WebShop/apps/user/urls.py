from django.conf.urls import *

from .views.auth import SignupScreen, SignupWholesaleDetailsScreen, SignupRetailDetailsScreen,\
    LoginZipcodeView, LoginView, RequestPasswordView, SetPasswordView
from .views.profile import AccountView, AccountAddressView
from .views.cart import ShoppingCartView, OrderHistoryView


urlpatterns = patterns('',

    # AUTHentication
    url(r'^login/$', LoginView.as_view(), name='login-route'),
    url(r'^login/zipcode/$', LoginZipcodeView.as_view(), name='login-zipcode-route'),
    url(r'^password/$', RequestPasswordView.as_view(), name="forgot-password-route"),
    url(r'^profile/setpassword/$', SetPasswordView.as_view(), name='change-password'),

    url(r'signup/$', SignupScreen.as_view(), name = 'signup-route'),
    url(r'signup/retail/details$', SignupRetailDetailsScreen.as_view(), name='signup-retail-details-route'),
    url(r'signup/wholesale/details$', SignupWholesaleDetailsScreen.as_view(), name='signup-wholesale-details-route'),
    url(r'activate/(?P<code>[0-9a-z-]+)', 'WebShop.apps.user.views.auth.activate', name="activation-route"),
    url(r'^logout/$', 'WebShop.apps.user.views.auth.logout', name="logout-route"),
    url(r'^checkmail/$', 'WebShop.apps.user.views.auth.check_mail', name='check-email-route'),

    (r'approve/(?P<token>\w+)', 'WebShop.apps.user.views.handler.approve'),
    (r'deny/(?P<token>\w+)', 'WebShop.apps.user.views.handler.deny'),


    # User settings

    url(r'^profile/$', AccountView.as_view(), name='profile-route'),
    url(r'^profile/addresses/$', AccountAddressView.as_view(), name='addresses-route'),

    url(r'cart/$', ShoppingCartView.as_view(), name="cart-route"),
    url(r'cart/refresh/$', 'WebShop.apps.user.views.cart.update_cart', name="refresh-cart-route"),
    url(r'cart/history/$', OrderHistoryView.as_view(), name="orders-route"),
    url(r'cart/add/$', 'WebShop.apps.user.views.cart.add_to_cart', name="add-to-cart-route"),
    url(r'cart/delete/(?P<id>\d+)/$', 'WebShop.apps.user.views.cart.delete_item', name="delete-from-cart-route"),


    # Shopping Cart
    (r'cart/cashier/$', 'WebShop.apps.user.views.order.cashier'),
    (r'cart/confirm/$', 'WebShop.apps.user.views.order.confirm_address'),
    # Order
    (r'order/submit/$', 'WebShop.apps.user.views.order.process_order')
)
 
