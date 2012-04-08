from WebShop.apps.user.models import Profile, Address, PasswordToken, RESETPASSWORDTOKEN
from WebShop.apps.user.forms import AccountForm, \
                            ChangePasswordForm, RequestPasswordForm, AddressForm
from WebShop.utils.etl import LEAST_ROLE, NORM_ROLE, HAS_RIGHTS
from WebShop.utils import mail
from django.conf import settings
from WebShop.apps.user.views import _attach_token
from django.contrib.auth.models import User
from django.contrib import auth
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

import datetime, simplejson

def index(request):
    if(request.user.is_anonymous()):
        return HttpResponseRedirect("/")
    else:
        return account(request)

def set_password(request):
    if request.method == 'POST' or request.user.is_authenticated():
        return HttpResponseRedirect("/")
    token = request.GET.get('token', None)
    if token:
        user = auth.authenticate(token = token, role = RESETPASSWORDTOKEN)
        if user:
            auth.login(request, user)
            form = ChangePasswordForm()
            return render_to_response('user/change_password.html', locals(), context_instance=RequestContext(request))
        else:
            title = _('Token Expired')
            message = _('The token for this requested password change has expired, please request again!')
            link_list = [('/main', _('Home')), ('/user/profile/password', _('forgot your password?'))]
            return render_to_response('generic_message.html', locals(), context_instance=RequestContext(request))
    else:
        title = _('Logged In')
        message = _('You are already logged in, want to change your password again? Proceed below!')
        link_list = [('/main', _('Home')), ('/user/profile/password', _('forgot your password?'))]
        return render_to_response('generic_message.html', locals(), context_instance=RequestContext(request))

def forgot_password(request):
    if request.method == 'POST':
        form = RequestPasswordForm(request.POST.copy())
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
                        title = _('Sorry')
                        short_message = _('bitte &Uuml;berpr&uuml;fen Sie nochmal Ihr Postfach!')
                        message = _('''Eine Passwort&auml;nderungsemail wurde bereits an die Email-Adresse: <b>%s</b> innerhalb der letzten 24 Stunden versendet.<br/><br/>
                            Um unsere Nutzer vor Spam
                            zu sch&uuml;tzen, k&ouml;nnen wir erst Morgen wieder eine neue Email senden, bitte kontakieren Sie uns doch direkt oder versuchen es Morgen noch einmal
                            !''') % form.cleaned_data['email']
                        return render_to_response('generic_message.html', locals(), context_instance=RequestContext(request))

                pt = _attach_token(user, role = RESETPASSWORDTOKEN)
                c = Context({'user': user, 'token': pt, 'host': request.META['HTTP_HOST']})
                mail.create_mail(_('%s Password Change Request' % settings.EMAIL_SUBJECT_PREFIX), settings.SERVER_EMAIL, form.cleaned_data['email'], 'changepassword', c)

            title = _('Wie Weiter?')
            short_message = _('&Uuml;berpr&uuml;fen Sie Ihr E-Mail Postfach <b>%s</b>!')  % form.cleaned_data['email']
            message = _('''Sie erhalten in K&uuml;rze von uns eine E-Mail, in der Sie den Link zum Neusetzen Ihres Passwortes finden!''')
            link_target = '/'
            link_title = 'Weiter'
            return render_to_response('generic_message.html', locals(), context_instance=RequestContext(request))
        return render_to_response('user/requestPWChange.html', locals(), context_instance=RequestContext(request))
    else:
        form = RequestPasswordForm()
        return render_to_response('user/requestPWChange.html', locals(), context_instance=RequestContext(request))

def change_password(request):
    if(request.user.is_anonymous()):
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST.copy())
        if form.is_valid():
            # Save password
            request.user.set_password(form.cleaned_data['password'])
            request.user.save()
            message = _(u'Your password has been updated.')
        else:
            message = _(u'Your password could not been updated, Password and Retype dont match.')

        return render_to_response('user/change_password.html', locals(), context_instance=RequestContext(request))
    form = ChangePasswordForm()
    return render_to_response('user/change_password.html', locals(), context_instance=RequestContext(request))

def _copy_shipping_form(dict):
	tmp = {}
	for k, v in dict.iteritems():
		tmp['%s2' % k] = v
	return ShippingForm(tmp)

def _get_user_data(user):
	profile = user.get_profile()
	try:
		billing = Address.objects.get(user=user, type='billing')
	except Address.DoesNotExist:
		billing = Address(user=user, type='billing')
		billing.save()

	try:
		shipping = Address.objects.get(user=user, type='shipping')
	except Address.DoesNotExist:
		params = billing.__dict__
		params.pop('_user_cache', None)
		params.pop('type', None)
		params.pop('_state', None)
		shipping = Address(type='shipping', **params)
		shipping.save()
	return user, profile, billing, shipping
    

def account(request):
	if request.user.is_anonymous(): return HttpResponseRedirect("/")
	user, profile, billing, shipping = _get_user_data(request.user)
	try:
		weekdays = simplejson.loads(profile.weekdays)
	except ValueError, e:
		# only needed until all profiles are converted to json
		try:
			weekdays = eval(profile.weekdays)
		except:
			weekdays = None
		profile.weekdays = simplejson.dumps(weekdays)
		profile.save()

	values = profile.__dict__
	values.update({'weekdays':weekdays, 'same_address': profile.same_address and 'Y' or 'N'})
	account_form = AccountForm(values)

	values = dict(map(lambda (k,v): ('billing-%s'%k, v), billing.__dict__.iteritems()))
	billing_form = AddressForm(values, prefix='billing')
	values = dict(map(lambda (k,v): ('shipping-%s'%k, v), shipping.__dict__.iteritems()))
	shipping_form = AddressForm(values, prefix='shipping')

	if(profile.role in HAS_RIGHTS):
		return render_to_response('user/account_wholesale.html', locals(), context_instance=RequestContext(request))
	else:
		return render_to_response('user/account_retail.html', locals(), context_instance=RequestContext(request))

def save_account(request):
	if request.user.is_anonymous() or request.method != 'POST':
		return HttpResponseRedirect("/")
	furl = request.GET.get("furl", None)
	user, profile, billing, shipping = _get_user_data(request.user)

	data = request.POST.copy()
	account_form = AccountForm(data)
	billing_form = AddressForm(data, prefix='billing')
	shipping_form = AddressForm(data, prefix='shipping')

	account_form.data['weekdays'] = simplejson.dumps(account_form.data.getlist('weekdays')) 
	for k,v in account_form.data.iteritems():
		setattr(profile, k, v)
	profile.save()

	for k,v in billing_form.data.iteritems():
		setattr(billing, k[8:], v)
	billing.save()

	for k,v in shipping_form.data.iteritems():
		setattr(shipping, k[9:], v)
	shipping.save()
	if furl:
		return  HttpResponseRedirect(furl)
	return account(request)