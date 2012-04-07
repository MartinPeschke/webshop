from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'getAllOrders/$', 'WebShop.apps.service.views.bo.getAllOrders'),
    (r'cha/$', 'WebShop.apps.service.views.bo.customer_has_account'), 
    (r'qscd/$', 'WebShop.apps.service.views.bo.quick_save_customer_data'),
    (r'scd/$', 'WebShop.apps.service.views.bo.save_customer_data'),
    (r'ac/$', 'WebShop.apps.service.views.bo.all_customers'),
    (r'bul/$', 'WebShop.apps.service.views.bo.backup_upload'),
    (r'brp/$', 'WebShop.apps.service.views.bo.backup_replay'),
    (r'ping/$', 'WebShop.apps.service.views.bo.ping'),
    
)
