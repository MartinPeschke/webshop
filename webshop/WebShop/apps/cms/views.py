from webshop.apps.cms.models import LinkGalleryItem
from webshop.apps.contrib.decorator import json

__author__ = 'Martin'



@json
def slideshowview(request, name):
    return LinkGalleryItem.objects.filter(slideshow__name = name)