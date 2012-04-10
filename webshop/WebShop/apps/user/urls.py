from django.conf.urls.defaults import *

urlpatterns = patterns('',

    # Login
    (r'rlogin', 'WebShop.apps.user.views.handler.rlogin'),
    (r'^login/$', 'WebShop.apps.user.views.auth.login'),
    (r'^login/zipcode/$', 'WebShop.apps.user.views.auth.login_zipcode'),
    (r'password/$', 'WebShop.apps.user.views.auth.forgot_password'),

    (r'signup/$', 'WebShop.apps.user.views.auth.signup'),
    (r'signup/details$', 'WebShop.apps.user.views.auth.signupdetails'),

    (r'^logout/$', 'WebShop.apps.user.views.handler.logout'),
    (r'^checkmail/$', 'WebShop.apps.user.views.auth.check_mail'),
    

    
    # User settings
    (r'^profile/$', 'WebShop.apps.user.views.profile.index'),
    
    (r'^profile/setpassword/$', 'WebShop.apps.user.views.profile.set_password'),
    (r'^profile/changepassword/$', 'WebShop.apps.user.views.profile.change_password'),
    (r'^profile/account/$', 'WebShop.apps.user.views.profile.account'),
    (r'^profile/account/save/$', 'WebShop.apps.user.views.profile.save_account'),

    # Register flow
    
    (r'registration/save/$', 'WebShop.apps.user.views.handler.save_registration'),

    (r'activate/(?P<code>\w+)', 'WebShop.apps.user.views.handler.activate'),
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
 
