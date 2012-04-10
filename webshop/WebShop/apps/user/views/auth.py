from django.http import HttpResponseRedirect
from django.contrib import auth, messages
from django.forms.util import ErrorList
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.utils.translation import ugettext as _, ugettext_lazy
from django.core.urlresolvers import reverse

import datetime, md5


from django.conf import settings
from django.contrib.auth.models import User

from WebShop.utils import mail
from WebShop.apps.contrib.decorator import json
from WebShop.apps.user.views import _attach_token
from WebShop.apps.user.forms import LoginEmailForm, LoginZipCodeForm, RequestPasswordForm, RegisterForm
from WebShop.apps.user.models import PasswordToken, RESETPASSWORDTOKEN


def login(request):
    """ Email Password Login"""
    forward_URL = request.REQUEST.get('forward_URL', '/')
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
    forward_URL = request.REQUEST.get('forward_URL', '/')
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
    if request.method == 'POST':
        form = RequestPasswordForm(request.POST)
        if form.is_valid():
            # send email
            try:
                user = User.objects.get(email = form.cleaned_data['email'])
            except User.DoesNotExist:
                pass
            else:
                try:
                    pt = PasswordToken.objects.get(user=user, role = RESETPASSWORDTOKEN)
                except PasswordToken.DoesNotExist:
                    pass
                else:
                    oneDay = datetime.timedelta(1)
                    if(datetime.datetime.now() - pt.create_time < oneDay):
                        messages.add_message(request, messages.ERROR, _('''Eine Passwort&auml;nderungsemail wurde bereits an die Email-Adresse: <b>%s</b> innerhalb der letzten 24 Stunden versendet.<br/><br/>
                            Um unsere Nutzer vor Spam
                            zu sch&uuml;tzen, k&ouml;nnen wir erst Morgen wieder eine neue Email senden, bitte kontakieren Sie uns doch direkt oder versuchen es Morgen noch einmal
                            !''') % form.cleaned_data['email'])
                    else:
                        pt = _attach_token(user, role = RESETPASSWORDTOKEN)
                        c = Context({'user': user, 'token': pt, 'host': request.META['HTTP_HOST']})
                        mail.create_mail(_('%s Password Change Request' % settings.EMAIL_SUBJECT_PREFIX), settings.SERVER_EMAIL, form.cleaned_data['email'], 'changepassword', c)
                        messages.add_message(request, messages.SUCCESS, _('''Sie erhalten in K&uuml;rze von uns eine E-Mail, in der Sie den Link zum Neusetzen Ihres Passwortes finden!'''))
    else:
        form = RequestPasswordForm()
    return render_to_response('user/auth/forgot_password.html', locals(), context_instance=RequestContext(request))


@json
def check_mail(request):
    email = request.GET.get('email', '')
    try:
        User.objects.get(email = email)
        result = _("Emailadresse bereits vergeben")
    except User.DoesNotExist:
        result = True
    except User.MultipleObjectsReturned:
        result = _("Emailadresse bereits vergeben")
    return result


def signup(request):
    if request.user.is_authenticated(): 
        return HttpResponseRedirect(reverse('WebShop.apps.explore.views.pages.main'))
    
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            email = register_form.cleaned_data['email']
            password = register_form.cleaned_data['password']
            user = User.objects.create_user(md5.new(email).hexdigest()[:30], email, password)
            user.is_active = False
            user.is_staff = False
            user.save()
            return HttpResponseRedirect(reverse('WebShop.apps.user.views.auth.signupdetails'))

    else:
        register_form = RegisterForm()
    return render_to_response('user/auth/signup.html', locals(), context_instance=RequestContext(request))



def signupdetails(request):
    if request.user.is_authenticated(): 
        return HttpResponseRedirect(reverse('WebShop.apps.explore.views.pages.main'))