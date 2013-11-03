# -*- coding: utf-8 -*-
import os
from django import template
from webshop.settings import MEDIA_ROOT, MEDIA_URL
from webshop.apps.cms.models import *

register = template.Library()

@register.filter
def menu_locale(en_obj, lang):
    try:
        lang_obj = MenuItem.objects.get(ref=str(en_obj.id), language=lang)
        title = lang_obj.title
    except:
        title = en_obj.title
    return '<a href="/%s/%s/">%s</a>' % (en_obj.category, en_obj.title, title)
