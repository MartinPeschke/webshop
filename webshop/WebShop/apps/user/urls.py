from django.conf.urls import *

from .views.auth import SignupScreen, SignupWholesaleDetailsScreen, SignupRetailDetailsScreen
from .views.profile import AccountView



urlpatterns = patterns('',

    # Login
    (r'rlogin', 'WebShop.apps.user.views.handler.rlogin'),
    url(r'^login/$', 'WebShop.apps.user.views.auth.login', name='login-route'),
    (r'^login/zipcode/$', 'WebShop.apps.user.views.auth.login_zipcode'),
    (r'^password/$', 'WebShop.apps.user.views.auth.forgot_password'),
    (r'^profile/setpassword/$', 'WebShop.apps.user.views.auth.set_password'),

    url(r'signup/$', SignupScreen.as_view(), name = 'signup-route'),
    url(r'signup/retail/details$', SignupRetailDetailsScreen.as_view(), name='signup-retail-details-route'),
    url(r'signup/wholesale/details$', SignupWholesaleDetailsScreen.as_view(), name='signup-wholesale-details-route'),

    url(r'^logout/$', 'WebShop.apps.user.views.auth.logout', name="logout-route"),
    (r'^checkmail/$', 'WebShop.apps.user.views.auth.check_mail'),
    

    
    # User settings
    (r'^profile/$', 'WebShop.apps.user.views.profile.index'),
    
    
    url(r'^profile/account/$', AccountView.as_view(), name='profile-route'),
    (r'^profile/account/save/$', 'WebShop.apps.user.views.profile.save_account'),


    url(r'activate/(?P<code>[0-9a-z-]+)', 'WebShop.apps.user.views.auth.activate', name="activation-route"),
    (r'approve/(?P<token>\w+)', 'WebShop.apps.user.views.handler.approve'),
    (r'deny/(?P<token>\w+)', 'WebShop.apps.user.views.handler.deny'),

    (r'orderFreeCatalog', 'WebShop.apps.user.views.handler.orderFreeCatalog'),

    # Shopping Cart
    (r'add_to_cart/$', 'WebShop.apps.user.views.order.add_to_cart'),
    (r'update_cart/$', 'WebShop.apps.user.views.order.update_cart'),
    (r'shopping_cart/$', 'WebShop.apps.user.views.order.shopping_cart'),
    (r'shopping_cart/delete/(?P<id>\d+)/$', 'WebShop.apps.user.views.order.delete_item'),
    (r'shopping_cart/cashier/$', 'WebShop.apps.user.views.order.cashier'),
    (r'shopping_cart/confirm/$', 'WebShop.apps.user.views.order.confirm_address'),
    
    # Order
    (r'order/submit/$', 'WebShop.apps.user.views.order.process_order')
)
 
