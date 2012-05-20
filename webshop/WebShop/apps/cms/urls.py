from django.conf.urls import *
from .views import slideshowview


urlpatterns = patterns('',
    # Shopping Cart
    url(r'get/(?P<name>[\w\d_]+)/', slideshowview, name="cms-get-route"),
)