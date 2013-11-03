import hashlib, datetime
import uuid
from django.contrib import messages
from django.template import Context
from django.conf import settings
from django.utils.translation import ugettext as _

from webshop.apps.user.models.password_token import PasswordToken, RESETPASSWORDTOKEN
from webshop.utils import mail

import logging
log = logging.getLogger(__name__)



def attach_token(user, role):
    try:
        token = PasswordToken.objects.get(user=user, role = role)
        token.delete()
    except PasswordToken.DoesNotExist:
        pass
    token = create_token(user, role)
    log.info("new token created %s", token)
    token.save()
    return token


def remove_token(user, role):
    try:
        token = PasswordToken.objects.get(user=user, role = role)
        token.delete()
    except PasswordToken.DoesNotExist:
        pass
    return token

def create_token(user, role):
    return PasswordToken(user=user, role=role, value = str(uuid.uuid4()))


def sendResetEmail(request, user):
    pt = attach_token(user, role = RESETPASSWORDTOKEN)
    c = Context({'user': user, 'token': pt, 'host': request.get_host()})
    mail.create_mail(_('%s Passwort zuruecksetzen') % settings.EMAIL_SUBJECT_PREFIX, settings.SERVER_EMAIL, user.email, 'changepassword', c)
    messages.add_message(request, messages.SUCCESS, _('''Sie erhalten in K&uuml;rze von uns eine E-Mail, in der Sie den Link zum Neusetzen Ihres Passwortes finden!'''))
