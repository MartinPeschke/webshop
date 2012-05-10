import hashlib
from django.conf import settings

from django.http import HttpRequest
from django.contrib.auth.models import User
from django.template.context import Context
from WebShop.apps.user.models import Profile
from WebShop.apps.user.models.password_token import APPROVALWHOLESALETOKEN, PasswordToken
from WebShop.apps.user.user_roles import ANONYMOUS_ROLE, userRoles, LEAST_ROLE, NORM_ROLE
from WebShop.utils import mail


__author__ = 'Martin'

def get_role(user):
    '''
    Get role from user
    '''
    if isinstance(user, HttpRequest):
       user = user.user

    if user.is_authenticated() and user.is_active:
        role = user.get_profile().role
    else:
        role = ANONYMOUS_ROLE
    return role



def create_user(email, password, role):
    user = User.objects.create_user(hashlib.md5(email).hexdigest()[:30], email, password)
    user.is_active = False
    user.is_staff = False
    if role not in userRoles:
        raise Exception("USER ROLE NOT RECOGNIZED %s", role)
    profile = Profile(user = user, role=role)
    user.save()
    profile.save()
    return user


def is_in_signup(user):
    if user.is_anonymous():
        return False
    try:
        profile = user.get_profile()
    except Profile.DoesNotExist:
        profile = Profile(user = user, role=LEAST_ROLE)
        profile.save()
    return profile.company_name is None or len(profile.company_name) == 0

def is_studio_user(user):
    if user.is_anonymous():
        return False
    profile = user.get_profile()
    return profile.role >= NORM_ROLE





def _send_register_mail(email, host, code, needs_approval):
    '''
    Send register mail
    '''
    c = Context({'username': email[:email.index('@')],
                 'email': email, 'needs_approval' : needs_approval,
                 'actLink': "%s%s" % ("http://%s%s" % (host, settings.ACTIVATE_ROOT), code)})
    mail.create_mail("%s Registration Confirmation" % settings.EMAIL_SUBJECT_PREFIX, settings.SERVER_EMAIL, email, 'activation_email', c)

def _send_approval_mail(host, user, token):
    '''
    Send per4 internal approval mail
    '''
    c = Context({'user':user, 'profile':user.get_profile(), 'approval_count':PasswordToken.objects.filter(role=APPROVALWHOLESALETOKEN).count(),
                 'approvalLink': "http://%s/user/approve/%s" % (host, token.value),
                 'denialLink': "http://%s/user/deny/%s" % (host, token.value)})
    mail.create_mail("%s Studio Kunde Bestaetigung Notwendig" % settings.EMAIL_SUBJECT_PREFIX, settings.SERVER_EMAIL, settings.SERVER_EMAIL, 'approval_email', c)
