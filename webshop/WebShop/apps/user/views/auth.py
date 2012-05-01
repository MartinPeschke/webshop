from django.http import HttpResponseRedirect
from django.contrib import auth, messages
from django.forms.util import ErrorList
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from django.core.urlresolvers import reverse

import datetime

from django.contrib.auth.models import User
from WebShop.apps import user

from WebShop.apps.lib.baseviews import  HTTPRedirect, BaseFormView
from WebShop.apps.contrib.decorator import json
from WebShop.apps.user.forms import LoginEmailForm, LoginZipCodeForm \
            , RequestPasswordForm, RegisterForm, ChangePasswordForm, WholesaleAccountForm

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

def login(request):
    """ Email Password Login"""
    forward_URL = request.REQUEST.get('forward_URL', reverse('WebShop.apps.explore.views.pages.main'))
    map = {'forward_URL':forward_URL}
    if request.method == 'POST':
            form = map['login_form'] = LoginEmailForm(request.POST)
            if form.is_valid():
                user = auth.authenticate(**form.cleaned_data)
                if user is None:
                    errors = form._errors.setdefault("email", ErrorList())
                    errors.append(ugettext_lazy('Sorry, please check your email and password.'))
                else:
                    if user.is_active:
                        auth.login(request, user)
                        if (request.session.get('cart', None)):
                            request.session['cart'].initUser(user)
                        return HttpResponseRedirect(forward_URL)
                    else:
                        errors = form._errors.setdefault("email", ErrorList())
                        errors.append(ugettext_lazy('Sorry, please activate your account.'))
    else:
        map['login_form'] = LoginEmailForm()
    return render_to_response('user/auth/login.html', map, context_instance=RequestContext(request))



def login_zipcode(request):
    """ CustomerNumber ZipCode Login"""
    forward_URL = request.REQUEST.get('forward_URL', reverse('WebShop.apps.explore.views.pages.main'))
    map = {'forward_URL':forward_URL}
    if request.method == 'POST':
        form = map['login_form'] = LoginZipCodeForm(request.POST)
            
        if form.is_valid():
            user = auth.authenticate(**form.cleaned_data)
            if user is None:
                errors = form._errors.setdefault("username", ErrorList())
                errors.append(ugettext_lazy('Sorry, please check your customer number or ZIP code.'))
            else:
                if user.is_active:
                    auth.login(request, user)
                    if (request.session.get('cart', None)):
                        request.session['cart'].initUser(user)
                    return HttpResponseRedirect(forward_URL)
                else:
                    errors = form._errors.setdefault("username", ErrorList())
                    errors.append(ugettext_lazy('Sorry, please activate your account.'))
    else:
        map['login_form'] = LoginZipCodeForm()
    return render_to_response('user/auth/login_zipcode.html', map, context_instance=RequestContext(request))

def forgot_password(request):
    form = RequestPasswordForm()
    if request.method == 'POST':
        _form = RequestPasswordForm(request.POST)
        if not _form.is_valid():
            form = _form
        else:
            try:
                user = User.objects.get(email = _form.data['email'])
            except User.DoesNotExist:
                form = _form
                errors = form._errors.setdefault("email", ErrorList())
                errors.append(ugettext_lazy('Unbekannte Emailadresse.'))
            else:
                try:
                    pt = PasswordToken.objects.get(user=user, role = RESETPASSWORDTOKEN)
                except PasswordToken.DoesNotExist:
                    sendResetEmail(request, user, _form)
                else:
                    oneDay = datetime.timedelta(1)
                    if datetime.datetime.now() - pt.create_time < oneDay:
                        messages.add_message(request, messages.ERROR, 
                            _('''Eine Passwort&auml;nderungsemail wurde bereits an die Email-Adresse: <b>%s</b> innerhalb der letzten 24 Stunden versendet.<br/><br/>
                            Um unsere Nutzer vor Spam
                            zu sch&uuml;tzen, k&ouml;nnen wir erst Morgen wieder eine neue Email senden, bitte kontakieren Sie uns doch direkt oder versuchen es Morgen noch einmal
                            !''') % _form.cleaned_data['email'])
                    else:
                        sendResetEmail(request, user, _form)
    else:
        pass
    return render_to_response('user/auth/forgot_password.html', locals(), context_instance=RequestContext(request))


def set_password(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('WebShop.apps.explore.views.pages.main'))
    if 'token' in request.GET:
        token = request.GET['token']
        
        user = auth.authenticate(token = token, role = RESETPASSWORDTOKEN)
        if user:
            form = ChangePasswordForm()

            if request.method == 'POST':
                _form = ChangePasswordForm(request.POST)

                print "-->", _form.is_valid()
                if not _form.is_valid():
                    form = _form
                else:
                    auth.login(request, user)
                    # Save password
                    request.user.set_password(_form.cleaned_data['password'])
                    request.user.save()
                    remove_token(user = user, role = RESETPASSWORDTOKEN)
                    messages.add_message(request, messages.SUCCESS, _('Passwort erfolgreich ge&auml;ndert!'))
            else:
                pass
        else:
            messages.add_message(request, messages.ERROR, _('The token for this requested password change has expired, please request again!'))
        return render_to_response('user/auth/change_password.html', locals(), context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect(reverse('WebShop.apps.explore.views.pages.main'))


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



class BaseSignUpView(BaseFormView):

    def pre_validate(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated() and user.is_active:
            raise HTTPRedirect(self.HOME_URL)

class SignupScreen(BaseSignUpView):
    template_name = 'user/auth/signup.html'
    form_cls = RegisterForm
    def pre_validate(self, request, *args, **kwargs):
        super(SignupScreen, self).pre_validate(request, *args, **kwargs)
        if is_in_signup(request.user):
            raise HTTPRedirect(self.get_user_signup_details_url(request))

    def on_success(self, request, cleaned_data):
        email = cleaned_data['email']
        password = cleaned_data['password']
        create_user(email, password, cleaned_data['role'])

        user = auth.authenticate(email = email, password = password)
        if user is not None:
            auth.login(request, user)
            raise HTTPRedirect(self.get_user_signup_details_url(request))
        else:
            messages.add_message(request, messages.ERROR, _('Ein Fehler ist aufgetreten!'))
            raise HTTPRedirect(self.SIGNUP_URL)



class SignupWholesaleDetailsScreen(BaseSignUpView):
    template_name = 'user/auth/signupdetails.html'
    form_cls = WholesaleAccountForm
    def pre_validate(self, request, *args, **kwargs):
        super(SignupWholesaleDetailsScreen, self).pre_validate(request, *args, **kwargs)
        if not is_in_signup(request.user):
            raise HTTPRedirect(self.SIGNUP_URL)

    def on_success(self, request, cleaned_data):
        user = request.user
        profile = user.get_profile()

        for field in profile._meta.fields:
            attr_name = field.attname
            if attr_name in cleaned_data:
                setattr(profile, attr_name, cleaned_data[attr_name])
        profile.is_signup_complete = True
        profile.save()

        register_token = attach_token(user, role = REGISTERNEWTOKEN)
        # Send Mail
        role = profile.role
        _send_register_mail(user.email, request.META['HTTP_HOST'], register_token.value, role in HAS_RIGHTS)
        if role in REQUIRES_APPROVAL:
            pt = attach_token(user, role = APPROVALWHOLESALETOKEN)
            _send_approval_mail(request.META['HTTP_HOST'], user, pt)
        raise HTTPRedirect(self.HOME_URL)

class SignupRetailDetailsScreen(SignupWholesaleDetailsScreen):
    pass





def activate(request, code):
    '''
    Activate user from url: http://host/user/activate/${code}/
    The code is generated by _make_username method.
    '''
    user = auth.authenticate(token = code, role = REGISTERNEWTOKEN)
    if(user):
        user.is_active = True
        user.save()
        auth.login(request, user)
        title = _('REGISTRATION - COMPLETED')
        messages.add_message(request, messages.SUCCESS, _('Congratulations! Your account has been activated.'))
    else:
        title = _('SORRY')
        messages.add_message(request, messages.ERROR, _('This Activation Code is invalid, maybe you already activated? Please check login or the link in your email and try again!'))
    return render_to_response('user/message.html', locals(), context_instance=RequestContext(request))