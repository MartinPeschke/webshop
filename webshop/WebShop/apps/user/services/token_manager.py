import md5, datetime
import logging
log = logging.getLogger(__name__)
from django.contrib import messages
from django.template import Context
from django.conf import settings
from django.utils.translation import ugettext as _, ugettext_lazy

from WebShop.apps.user.models import PasswordToken, RESETPASSWORDTOKEN
from WebShop.utils import mail




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
    token = PasswordToken(user=user, role=role)
    token.value = md5.new(str(datetime.datetime.now())+user.password).hexdigest()
        # added the hash of password so knowing time of creation is not enough to guess token value
    return token


def sendResetEmail(request, user, form):
    pt = attach_token(user, role = RESETPASSWORDTOKEN)
    c = Context({'user': user, 'token': pt, 'host': request.get_host()})
    mail.create_mail(_('%s Passwort zuruecksetzen') % settings.EMAIL_SUBJECT_PREFIX, settings.SERVER_EMAIL, form.cleaned_data['email'], 'changepassword', c)
    messages.add_message(request, messages.SUCCESS, _('''Sie erhalten in K&uuml;rze von uns eine E-Mail, in der Sie den Link zum Neusetzen Ihres Passwortes finden!'''))
