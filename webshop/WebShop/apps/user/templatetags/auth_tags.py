from django import template
from WebShop.apps.user.lib import is_in_signup, is_studio_user
from WebShop.apps.user.user_roles import userRoles

register = template.Library()

@register.filter
def is_user_in_signup(user):
    return is_in_signup(user)

@register.filter
def is_studio(user):
    return is_studio_user(user)


@register.filter
def getRoleName(role):
    return userRoles.get(role,'-')

@register.filter
def getRoleNameForUser(user):
    return userRoles.get(user.get_profile().role,'')