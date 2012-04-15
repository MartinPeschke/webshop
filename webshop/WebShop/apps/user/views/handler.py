from django.conf import settings
from WebShop.apps.contrib.decorator import json
from WebShop.apps.user.forms import LoginEmailForm, LoginZipCodeForm,\
    RegisterForm, AccountForm, AddressForm, OrderFreeCatalogForm, ValidationError
from WebShop.apps.user.models import Profile, Address, PasswordToken, APPROVALWHOLESALETOKEN, REGISTERNEWTOKEN

from WebShop.apps.user.services.token_manager import attach_token


from WebShop.utils.etl import NO_RIGHTS, HAS_RIGHTS, userRoles, NORM_ROLE, LEAST_ROLE
from WebShop.utils import mail

from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.forms.util import ErrorList
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context
from django.utils.translation import gettext_lazy as _, ugettext_lazy
from django.contrib.sessions.models import Session
from django.utils.safestring import mark_safe



from time import time
import os, md5, simplejson, pickle

#===============================================================================
# TODO : How to Merge Carts? How to retrieve previous session? when anon user has a new session :/
#===============================================================================
@json
def rlogin(request):
    '''
    Login method call for AJAX
    '''
    map = {}
    zip = False
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(email=email, password=password)

    if user is None:
        user = auth.authenticate(username=email, password=password)
        zip = True

    if user is not None:
        if user.is_active:
            auth.login(request, user)
            if (request.session.get('cart', None)):
                request.session['cart'].initUser(user)
            request.session['zip'] = zip      
            map['result'] = True
        else:
            map['result'] = False
            map['error'] = str(_('Sorry, please activate your account.'))
    else:
        map['result'] = False
        map['error'] = str(_('Sorry, please check your email and password.'))
    return map




def logout(request):
    auth.logout(request)
    
    # Try to delete cart info.
    try:
        del request.session['cart']
    except:
        pass

    referer = request.META.get('HTTP_REFERER', '/')
    if "/user/" in referer:
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect(referer)

@json
def check_mail(request):
    '''
    AJAX method call for checking email exist.
    '''
    map = {}
    email = request.POST.get('email', '')
    try:
        User.objects.get(email=email)
        map['result'] = False
    except User.DoesNotExist:
        map['result'] = True
    return map

def registration(request):
    '''
    Display basic register form and validate it.
    '''
    if request.user.is_authenticated(): 
        return HttpResponseRedirect("/")
    
    if request.method == 'POST':
        register_form = RegisterForm(request.POST.copy())

        role = request.POST.get('role', None)
        if (role in NO_RIGHTS + HAS_RIGHTS) and register_form.is_valid():
            account_form = AccountForm()
            billing_form = AddressForm(prefix='billing')
            shipping_form = AddressForm(prefix='shipping')
            
            request.session['email'] = register_form.data['email']
            request.session['role'] = role
            request.session['password'] = register_form.data['password']
            use_ssl = register_form.data.get('use_ssl', False)
            
            registration = True
            return render_to_response('user/register_%s.html' % userRoles[role].lower(), locals(), context_instance=RequestContext(request))
        else:
            return render_to_response('user/register_new.html', locals(), context_instance=RequestContext(request))        
    
    else:
        studio = request.REQUEST.get('studio', '')
        register_form = RegisterForm()
        if(request.session.get('duplicate_email', False)):
            register_form = RegisterForm({'email':request.session.get('email')})
            register_form.is_valid()
#===============================================================================
#            del request.session['duplicate_email']
#===============================================================================
        return render_to_response('user/register_new.html', locals(), context_instance=RequestContext(request))

def save_registration(request):
    if(request.user.is_authenticated() or 'email' not in request.session): 
        return HttpResponseRedirect("/")
    
    if request.method != 'POST':
        return HttpResponseRedirect("/")
    else:
        role = request.session.get('role', 'E')
        registration = True       

        account_form = AccountForm(request.POST.copy())
        billing_form = AddressForm(request.POST.copy(), prefix ='billing')
        shipping_form = AddressForm(request.POST.copy(), prefix ='shipping')
        
        shipping_form._errors = {}
        valid = account_form.is_valid() and billing_form.is_valid()
        
        if(role not in HAS_RIGHTS):
            account_form._errors.pop('opening_hours', None)
            account_form._errors.pop('weekdays', None)
            account_form._errors.pop('vat_id', None)
            account_form._errors.pop('company_name', None)
            
        
        if not (account_form.is_valid() and billing_form.is_valid()):
            return render_to_response('user/register_%s.html' % userRoles[role].lower(), locals(), context_instance=RequestContext(request))
        else:
            # use billing if not entered shipping
            if(not (shipping_form.data.get('street') and
                    shipping_form.data.get('city') and 
                    shipping_form.data.get('zip') and 
                    shipping_form.data.get('country') and 
                    shipping_form.data.get('tel'))):
                    shipping_form = AddressForm(dict([(k.replace('billing', 'shipping'),v) for k,v in billing_form.data.iteritems()]), prefix='shipping')

            try:
                user = _create_user(request.session['email'], request.session['password'])
            except:
                request.session['duplicate_email'] = True                
                return HttpResponseRedirect('/user/registration/')
            else:
                # Create Profile
                profile = Profile(user = user)
                billing = Address(user = user, type = 'billing')
                shipping = Address(user = user, type = 'shipping')

                account_form.data['weekdays'] = simplejson.dumps(account_form.data.getlist('weekdays'))
                for k,v in account_form.data.iteritems():
                    setattr(profile, k, v)
                profile.role = 'E'
                profile.save()
                
                data = filter(lambda (k,v): k.startswith('billing-'), billing_form.data.iteritems())
                for k,v in data:
                    setattr(billing, k[8:], v)
                billing.save()
            
                data = filter(lambda (k,v): k.startswith('shipping-'), shipping_form.data.iteritems())
                for k,v in data:
                    setattr(shipping, k[9:], v)
                shipping.save()

                register_token = attach_token(user, role = REGISTERNEWTOKEN)
                # create & save approval token
                pt = attach_token(user, role = APPROVALWHOLESALETOKEN)
                # Send Mail
                _send_register_mail(request.session['email'], request.session['password'], request.META['HTTP_HOST'], register_token.value, role in HAS_RIGHTS)
                if(role in HAS_RIGHTS):
                    _send_approval_mail(request.META['HTTP_HOST'], user, pt)
            return render_to_response('user/register_%s_done.html' % userRoles[role].lower(), locals(), context_instance=RequestContext(request))

def _send_register_mail(email, password, host, code, needs_approval):
    '''
    Send register mail
    '''
    c = Context({'username': email[:email.index('@')],
        'email': email,
        'password': password, 'needs_approval' : needs_approval,
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


def _create_user(email, password):
    user = User.objects.create_user(md5.new(email).hexdigest()[:30], email, password)
    user.is_active = False
    user.is_staff = False
    user.save()
    return user

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
    else:
        message = _('This Activation Code is invalid, maybe you already activated? Please check login or the link in your email and try again!')
    return render_to_response('user/activate.html', locals(), context_instance=RequestContext(request))

def approve(request, token):
    '''
    Activate user from url: http://host/user/activate/${code}/
    The code is generated by _make_username method.
    '''

    user = auth.authenticate(token=token, role = APPROVALWHOLESALETOKEN)
    if(user):
        profile = user.get_profile()
        profile.role = NORM_ROLE
        profile.save()
        user.message_set.create(message=str(_('You have been approved for Wholesale access, enjoy your shopping!')))        
    else:
        message = _('This Approval Code is invalid, maybe you already approved this user?')


    approved_users = User.objects.filter(profile__role='K').order_by('id')
    
    profiles = dict([(p.user_id, p) for p in Profile.objects.filter(user__in = approved_users)])
    address = dict([(a.user_id, a) for a in Address.objects.filter(user__in=approved_users, type='billing')])

    for a in approved_users:
        a.profile = profiles.get(a.id, False)
        a.address = address.get(a.id, False)
    
    return render_to_response('user/approved.html', locals(), context_instance=RequestContext(request))

def deny(request, token):
    '''
    Activate user from url: http://host/user/activate/${code}/
    The code is generated by _make_username method.
    '''
    user = auth.authenticate(token=token, role = APPROVALWHOLESALETOKEN)
    if(user):
        user.message_set.create(message=str(_('Sorry, we could not approve your Wholesale Access request, please call us or contact us by email to clarify.')))
    else:
        message = _('This Approval Code is invalid, maybe you already denied this request?')
    return render_to_response('user/activate.html', locals(), context_instance=RequestContext(request))

def orderFreeCatalog(request):
    if request.method == 'GET':
        form = OrderFreeCatalogForm()
    if request.method == 'POST':
        form = OrderFreeCatalogForm(request.POST.copy())
        if form.is_valid():
            c = Context({'form': form,
                         'user': request.user,})
            mail.create_mail("%s Order Free Catalog" % settigs.EMAIL_SUBJECT_PREFIX, settings.SERVER_EMAIL, settings.ORDER_MAIL, 'orderFreeCatalog', c)
            return render_to_response('user/orderFreeCatalogDone.html', locals(), context_instance=RequestContext(request))
        else:
            return render_to_response('user/orderFreeCatalog.html', locals(), context_instance=RequestContext(request))
    return render_to_response('user/orderFreeCatalog.html', locals(), context_instance=RequestContext(request))