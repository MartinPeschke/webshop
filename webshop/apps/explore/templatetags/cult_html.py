import os
from django import template
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.safestring import mark_safe

from django.conf import settings
from WebShop.apps.explore.models import *
from WebShop.utils.etl import NO_RIGHTS, HAS_RIGHTS, userRoles

register = template.Library()


@register.simple_tag
def req_input_tag(name, id = None, size=25, type='text', value='', class_=''):
    if not id: id = name
    if isinstance(value,dict):
       value = value.get(name, '') 
    return  """
        <div class="req_input">
            <div style="position:relative;float:left;  font-size:32px; color: #ffd241;line-height: 32px;">[</div>
            <input size="%(size)s" style="position:relative;float:left; margin: 9px -3px 10px -3px;height:17px;" id="%(id)s" type="%(type)s" name="%(name)s" value="%(value)s" class="%(class)s"/>
            <div style="position:relative;float:left; font-size:32px; color: #ffd241;line-height: 32px;">]</div>
        </div>                
    """ % {'id':id, 'name':name, 'type':type, 'size':size, 'value':value, 'class':class_} 

@register.simple_tag
def rounded_corners():
    return """<img src="/media/images/top_right_corner.png" style="position: absolute; top:0px; right:0px;"/>
            <img src="/media/images/bot_right_corner.png" style="position: absolute; bottom:0px; right:0px;"/>
            <img src="/media/images/bot_left_corner.png" style="position: absolute; bottom:0px; left:0px;"/>
            <img src="/media/images/top_left_corner.png" style="position: absolute; top:0px; left:0px;"/>"""
