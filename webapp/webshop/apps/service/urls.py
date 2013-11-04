from django.conf.urls import *

urlpatterns = patterns('',
    (r'getAllOrders/$', 'webshop.apps.service.views.bo.getAllOrders'),
    (r'cha/$', 'webshop.apps.service.views.bo.customer_has_account'),
    (r'qscd/$', 'webshop.apps.service.views.bo.quick_save_customer_data'),
    (r'scd/$', 'webshop.apps.service.views.bo.save_customer_data'),
    (r'ac/$', 'webshop.apps.service.views.bo.all_customers'),
    (r'bul/$', 'webshop.apps.service.views.bo.backup_upload'),
    (r'brp/$', 'webshop.apps.service.views.bo.backup_replay'),
    (r'ping/$', 'webshop.apps.service.views.bo.ping'),
    
)
