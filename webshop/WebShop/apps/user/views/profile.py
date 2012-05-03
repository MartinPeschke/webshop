from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy
import  simplejson
from WebShop.apps.user.forms.profile import AddressForm

from WebShop.apps.user.models.address import Address

from WebShop.apps.lib.baseviews import  BaseLoggedInView, BaseFormView, HTTPRedirect

from django.forms.models import modelformset_factory


class AccountView(BaseLoggedInView):
    template_name = 'user/profile/index.html'
    def get(self, request, *args, **kwargs):
        pass

class AccountAddressView(BaseFormView):
    template_name = 'user/profile/addresses.html'
    form_cls = AddressForm

    def get_form_instance(self, request, *args, **kwargs):
        AddressFormSet = modelformset_factory(Address)
        formset = AddressFormSet(queryset = Address.objects.filter(user=request.user))
        return formset

    def on_success(self, request, cleaned_data):
        params = {}
        for k, value in cleaned_data.items():
            type, field = k.split("_", 1)
            address_field = params.setdefault(type, {})
            address_field[field] = value

        for t, fields in params.items():
            try:
                address = Address.objects.get(user=request.user, type = t)
            except Address.DoesNotExist:
                address = Address(user=request.user, type = t)
            for field, value in fields.items():
                setattr(address, 'field', value)
            address.save()
        raise HTTPRedirect(request.get_full_path())






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
    account_form = WholesaleAccountForm(values)

    values = dict(map(lambda (k,v): ('billing-%s'%k, v), billing.__dict__.iteritems()))
    billing_form = AddressForm(values, prefix='billing')
    values = dict(map(lambda (k,v): ('shipping-%s'%k, v), shipping.__dict__.iteritems()))
    shipping_form = AddressForm(values, prefix='shipping')

    if(profile.role in HAS_RIGHTS):
        return render_to_response('user/account_wholesale.html', locals(), context_instance=RequestContext(request))
    else:
        return render_to_response('user/account_retail.html', locals(), context_instance=RequestContext(request))











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