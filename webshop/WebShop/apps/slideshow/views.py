from WebShop.apps.contrib.decorator import json
from WebShop.apps.slideshow.models import  SlideShowItem

__author__ = 'Martin'



@json
def slideshowview(request, name):
    return SlideShowItem.objects.filter(slideshow__name = name)