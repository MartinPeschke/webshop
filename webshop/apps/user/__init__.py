from WebShop.utils.etl import ANONYMOUS_ROLE
from django.http import HttpRequest


simple_role = {'F':'E', 'E':'E', 'X':'E', 'K':'K', 'P':'K'}

def get_role(user):
    '''
    Get role from user
    '''    
    if(isinstance(user, HttpRequest)):
       user = user.user
       
    if user.is_authenticated():
        role = user.get_profile().role
    else:
        role = ANONYMOUS_ROLE
    return role