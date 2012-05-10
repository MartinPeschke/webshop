from django.core.urlresolvers import reverse
import simplejson
from WebShop.apps.contrib.countries.models import Country
from WebShop.apps.user.forms.auth import WholesaleAccountForm, RetailAccountForm
from WebShop.apps.user.forms.profile import AccountRetailDetailsForm, AccountWholesaleDetailsForm
from WebShop.apps.user.lib import is_studio_user

from WebShop.apps.user.models.address import Address, Language, AddressType
from WebShop.apps.user.forms import AddressesForm
from WebShop.apps.lib.baseviews import  BaseLoggedInView, BaseFormView, HTTPRedirect


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



class AccountAddressView(BaseLoggedInView, BaseFormView):
    template_name = 'user/profile/addresses.html'
    form_cls = AddressesForm

    def get_form_instance(self, request, *args, **kwargs):
        params = {}
        addresses = Address.objects.filter(user=request.user).values()
        if len(addresses):
            for address_map in addresses:
                t = AddressType.objects.get(pk = address_map.pop('type_id')).name
                address_map['language'] = Language.objects.get(pk=address_map.pop('language_id')).code
                address_map['country'] = Country.objects.get(pk=address_map.pop('country_id')).iso
                params.update({"{}_{}".format(t, k):v for k,v in address_map.items()})
        else:
            params = {}
            params['billing_language'] = params['shipping_language']= 'de'
            params['billing_country'] = params['shipping_country'] = 'DE'
        return self.form_cls(initial = params)

    def on_success(self, request, cleaned_data):
        params = {}
        for k, value in cleaned_data.items():
            type, field = k.split("_", 1)
            address_field = params.setdefault(type, {})
            address_field[field] = value

        for t, fields in params.items():
            try:
                type = AddressType.objects.get(name = t)
                address = Address.objects.get(user=request.user, type = type)
            except Address.DoesNotExist:
                address = Address(user=request.user, type = type)

            for field, value in fields.items():
                if field=='language':
                    value = Language.objects.get(pk=value)
                elif field=='country':
                    value = Country.objects.get(pk=value)
                setattr(address, field, value)
            address.save()
        raise HTTPRedirect(request.get_full_path())


class ProfileView(BaseLoggedInView, BaseFormView):
    template_name = 'user/profile/index.html'
    def get_validation_form_instance(self, request):
        if is_studio_user(request.user):
            return AccountWholesaleDetailsForm(request.POST)
        else:
            return AccountRetailDetailsForm(request.POST)

    def get_form_instance(self, request, *args, **kwargs):
        initial = request.user.get_profile().json_equivalent()
        try:
            initial['weekdays'] = simplejson.loads(initial['weekdays'])
        except:
            pass
        if is_studio_user(request.user):
            return AccountWholesaleDetailsForm(initial = initial)
        else:
            return AccountRetailDetailsForm(initial = initial)
    def on_success(self, request, cleaned_data):
        profile = request.user.get_profile()
        for field in profile._meta.fields:
            attr_name = field.attname
            if attr_name in cleaned_data:
                setattr(profile, attr_name, cleaned_data[attr_name])
        profile.weekdays = simplejson.dumps(cleaned_data['weekdays'])
        profile.save()
        raise HTTPRedirect(reverse('profile-route'))
