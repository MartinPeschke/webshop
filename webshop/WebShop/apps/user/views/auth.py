from django.http import HttpResponseRedirect
from django.contrib import auth, messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy

import datetime

from django.contrib.auth.models import User
import simplejson
from WebShop.apps import user

from WebShop.apps.lib.baseviews import  HTTPRedirect, BaseFormView, BaseView
from WebShop.apps.contrib.decorator import json
from WebShop.apps.user.forms import LoginEmailForm, LoginZipCodeForm \
            , RequestPasswordForm, RegisterForm, ChangePasswordForm, WholesaleAccountForm, RetailAccountForm

from WebShop.apps.user.models.password_token import PasswordToken, RESETPASSWORDTOKEN, REGISTERNEWTOKEN, APPROVALWHOLESALETOKEN

from WebShop.apps.user.services.token_manager import  sendResetEmail, remove_token, attach_token
from WebShop.apps.user.lib import is_in_signup, create_user, _send_register_mail, _send_approval_mail
from WebShop.apps.user.user_roles import HAS_RIGHTS, REQUIRES_APPROVAL

def logout(request):
    auth.logout(request)
    request.session.pop('cart', None)
    referer = request.META.get('HTTP_REFERER', '/')
    if "/user/" in referer:
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect(referer)


@json
def check_mail(request):
    email = request.GET.get('email')
    if not email:
        return False
    try:
        User.objects.get(email = email)
        result = _("Emailadresse bereits vergeben")
    except User.DoesNotExist:
        result = True
    except User.MultipleObjectsReturned:
        result = _("Emailadresse bereits vergeben")
    return result



class BaseAuthView(BaseFormView):
    template_name = 'user/auth/base.html'
    def pre_validate(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated() and user.is_active:
            raise HTTPRedirect(self.HOME_URL)


class LoginView(BaseAuthView):
    form_cls = LoginEmailForm

    def on_success(self, request, cleaned_data):
        user = cleaned_data['user']
        auth.login(request, user)
        if request.session.get('cart', None):
            request.session['cart'].initUser(user)
        if is_in_signup(user):
            messages.add_message(request, messages.ERROR, _('Bitte Registrierung beenden!'))
            raise HTTPRedirect(self.SIGNUP_URL)
        furl = request.REQUEST.get('furl', self.HOME_URL)
        raise HTTPRedirect(furl)

class LoginZipcodeView(LoginView):
    form_cls = LoginZipCodeForm

class RequestPasswordView(LoginView):
    form_cls = RequestPasswordForm
    def on_success(self, request, cleaned_data):
        user = cleaned_data['user']
        try:
            pt = PasswordToken.objects.get(user=user, role = RESETPASSWORDTOKEN)
        except PasswordToken.DoesNotExist:
            sendResetEmail(request, user)
        else:
            oneDay = datetime.timedelta(1)
            if datetime.datetime.now() - pt.create_time < oneDay:
                messages.add_message(request, messages.ERROR,
                    _('''Eine Passwort&auml;nderungsemail wurde bereits an die Email-Adresse: <b>%s</b> innerhalb der letzten 24 Stunden versendet.<br/><br/>
                    Um unsere Nutzer vor Spam zu sch&uuml;tzen, k&ouml;nnen wir erst Morgen wieder eine neue Email senden, bitte kontakiere uns doch direkt oder versuche es Morgen noch einmal!''') % user.email)
            else:
                sendResetEmail(request, user)
        raise HTTPRedirect(request.get_full_path())


class SetPasswordView(BaseFormView):
    form_cls = RegisterForm
    def pre_validate(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated():
            raise HTTPRedirect(self.HOME_URL)
        if 'token' in request.GET:
            token = request.GET['token']
            setattr(self, 'user', auth.authenticate(token = token, role = RESETPASSWORDTOKEN))
        if getattr(self, 'user', None) is None:
            messages.add_message(request, messages.ERROR, _('The token for this requested password change has expired, please request again!'))
            raise HTTPRedirect(self.HOME_URL)

    def on_success(self, request, cleaned_data):
        auth.login(request, user)
        # Save password
        request.user.set_password(cleaned_data['password'])
        request.user.save()
        remove_token(user = user, role = RESETPASSWORDTOKEN)
        messages.add_message(request, messages.SUCCESS, _('Passwort erfolgreich ge&auml;ndert!'))
        return render_to_response('user/auth/change_password.html', locals(), context_instance=RequestContext(request))

class SignupScreen(BaseAuthView):
    form_cls = RegisterForm
    def pre_validate(self, request, *args, **kwargs):
        if is_in_signup(request.user):
            raise HTTPRedirect(self.get_user_signup_details_url(request))

    def on_success(self, request, cleaned_data):
        email = cleaned_data['email']
        password = cleaned_data['password']
        role = cleaned_data['role']
        create_user(email, password, role)

        user = auth.authenticate(email = email, password = password)
        if user is not None:
            # send activation email right away
            register_token = attach_token(user, role = REGISTERNEWTOKEN)
            _send_register_mail(user.email, request.META['HTTP_HOST'], register_token.value, role in REQUIRES_APPROVAL)
            auth.login(request, user)
            raise HTTPRedirect(self.get_user_signup_details_url(request))
        else:
            messages.add_message(request, messages.ERROR, _('Ein Fehler ist aufgetreten!'))
            raise HTTPRedirect(self.SIGNUP_URL)



class SignupWholesaleDetailsScreen(BaseAuthView):
    template_name = 'user/auth/finish_signup.html'
    form_cls = WholesaleAccountForm

    def pre_validate(self, request, *args, **kwargs):
        if not is_in_signup(request.user):
            raise HTTPRedirect(self.SIGNUP_URL)

    def on_success(self, request, cleaned_data):
        user = request.user
        profile = user.get_profile()
        for field in profile._meta.fields:
            attr_name = field.attname
            if attr_name in cleaned_data:
                setattr(profile, attr_name, cleaned_data[attr_name])
        profile.save()

        # Send Mail
        role = profile.role
        if role in REQUIRES_APPROVAL:
            pt = attach_token(user, role = APPROVALWHOLESALETOKEN)
            _send_approval_mail(request.META['HTTP_HOST'], user, pt)
        raise HTTPRedirect(self.HOME_URL)

class SignupRetailDetailsScreen(SignupWholesaleDetailsScreen):
    form_cls = RetailAccountForm
    pass


class ActivateAccountView(BaseView):
    template_name = 'user/auth/signup_finished.html'
    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = auth.authenticate(token = code, role = REGISTERNEWTOKEN)
        if user:
            user.is_active = True
            user.save()
            auth.login(request, user)
            if is_in_signup(user):
                messages.add_message(request, messages.SUCCESS, _('Congratulations! Your account has been activated. Please finish your registration!'))
                raise HTTPRedirect(self.get_user_signup_details_url(request))
            else:
                title = _('REGISTRATION - COMPLETED')
                messages.add_message(request, messages.SUCCESS, _('Congratulations! Your account has been activated.'))
        else:
            title = _('SORRY')
            messages.add_message(request, messages.ERROR, _('This Activation Code is invalid, maybe you already activated? Please check login or the link in your email and try again!'))
        return {'title':title}