from django import template
from WebShop.apps.user.lib import is_in_signup

register = template.Library()

@register.filter
def is_user_in_signup(user):
    return is_in_signup(user)