import json

from django.contrib import messages
from django.utils.translation import ugettext as _

from webshop.apps.contrib.countries.models import Country
from webshop.apps.user.forms.profile import AccountRetailDetailsForm, AccountWholesaleDetailsForm
from webshop.apps.user.lib import is_studio_user
from webshop.apps.user.models.address import Address, Language, AddressType
from webshop.apps.user.forms import AddressesForm
from webshop.apps.lib.baseviews import  BaseLoggedInView, BaseFormView, HTTPRedirect


def _get_user_data(user):
    profile = user.get_profile()
    try:
        billing = Address.objects.get(user=user, type__name='billing')
    except Address.DoesNotExist:
        billing = None
    try:
        shipping = Address.objects.get(user=user, type__name='shipping')
    except Address.DoesNotExist:
        shipping = None
    return user, profile, billing, shipping



class BaseAccountAddressView(BaseLoggedInView, BaseFormView):
    template_name = 'user/profile/addresses.html'
    form_cls = AddressesForm

    def get_form_instance(self, request, *args, **kwargs):
        params = {'same_address':request.user.get_profile().same_address}
        addresses = Address.objects.filter(user=request.user).values()
        if len(addresses):
            for address_map in addresses:
                t = AddressType.objects.get(pk = address_map.pop('type_id')).name
                try:
                    address_map['language'] = Language.objects.get(pk=address_map.pop('language_id')).code
                except Language.DoesNotExist:
                    address_map['language'] = Language.objects.get(is_default = True).code
                try:
                    address_map['country'] = Country.objects.get(pk=address_map.pop('country_id')).iso
                except Country.DoesNotExist:
                    address_map['country'] = Country.objects.get(is_default = True).iso
                params.update({"{}_{}".format(t, k):v for k,v in address_map.items()})
        else:
            params = {}
            params['billing_language'] = params['shipping_language'] \
                = Language.objects.get(is_default = True).code
            params['billing_country'] = params['shipping_country'] \
                = Country.objects.get(is_default = True).iso
            params['billing_name'] = params['shipping_name'] = request.user.get_profile().get_pretty_name()
        return self.form_cls(initial = params)

    def on_success(self, request, cleaned_data):
        params = {}

        profile = request.user.get_profile()
        profile.same_address = cleaned_data['same_address']
        profile.save()

        for k, value in cleaned_data.items():
            type, field = k.split("_", 1)
            address_field = params.setdefault(type, {})
            address_field[field] = value


        for t, fields in params.items():
            if t in ['shipping', 'billing']:
                type = AddressType.objects.get(name = t)
                try:
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



class AccountAddressView(BaseAccountAddressView):
    def on_success(self, request, cleaned_data):
        try:
            return super(AccountAddressView, self).on_success(request, cleaned_data)
        except HTTPRedirect:
            messages.add_message(request, messages.SUCCESS, _('&Auml;nderungen gespeichert!'))
            raise


class ProfileView(BaseLoggedInView, BaseFormView):
    template_name = 'user/profile/index.html'
    def get_validation_form_instance(self, request):
        if is_studio_user(request.user):
            return AccountWholesaleDetailsForm(request.POST)
        else:
            return AccountRetailDetailsForm(request.POST)

    def get_form_instance(self, request, *args, **kwargs):
        initial = request.user.get_profile().json_equivalent()
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
        profile.weekdays = json.dumps(cleaned_data.get('weekdays') or [])
        profile.save()
        messages.add_message(request, messages.SUCCESS, _('&Auml;nderungen gespeichert!'))
        raise HTTPRedirect(request.get_full_path())
