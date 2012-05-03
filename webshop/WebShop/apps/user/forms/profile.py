from operator import attrgetter
from django import forms
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms.models import ModelForm

from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy
from WebShop.apps.user.models.address import Address

__author__ = 'Martin'

from WebShop.apps.contrib.countries.models import Country
COUNTRIES = map(attrgetter('iso', 'printable_name'), Country.objects.all())


class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ('user',)
        fields = ('language', 'country', 'type')
    def __init__(self, *args, **kwargs):
        def __init__(self, *args, **kwargs):
            self.helper = FormHelper()
            self.helper.form_tag = False
            self.helper.layout = Layout(
                Fieldset(
                    ugettext_lazy("Adresse"),
                    'street',
                    'city',
                    'zip',
                    'country',
                    'language',
                    'tel',
                    'mobile',
                    'fax'
                )
            )
            super(AddressesForm, self).__init__(*args, **kwargs)


        super(AddressForm, self).__init__(*args, **kwargs)


class AddressesForm(forms.Form):
    billing_street = forms.CharField(label = ugettext_lazy('Strasse'))
    billing_city = forms.CharField(label = ugettext_lazy('Stadt'))
    billing_zip = forms.CharField(label = ugettext_lazy('PLZ'))
    billing_country = forms.ChoiceField(choices=COUNTRIES, widget=Select, label = ugettext_lazy('Land'))
    billing_language = forms.ChoiceField(choices=settings.LANGUAGES, widget=Select, label = ugettext_lazy('Bevorzugte Sprache'))
    billing_tel = forms.CharField(label = ugettext_lazy('Telefon'))
    billing_mobile = forms.CharField(label = ugettext_lazy('Mobil'), required=False)
    billing_fax = forms.CharField(label = ugettext_lazy('Fax'), required=False)

    shipping_street = forms.CharField(label = ugettext_lazy('Strasse'))
    shipping_city = forms.CharField(label = ugettext_lazy('Stadt'))
    shipping_zip = forms.CharField(label = ugettext_lazy('PLZ'))
    shipping_country = forms.ChoiceField(choices=COUNTRIES, widget=Select, label = ugettext_lazy('Land'))
    shipping_language = forms.ChoiceField(choices=settings.LANGUAGES, widget=Select, label = ugettext_lazy('Bevorzugte Sprache'))
    shipping_tel = forms.CharField(label = ugettext_lazy('Telefon'))
    shipping_mobile = forms.CharField(label = ugettext_lazy('Mobil'), required=False)
    shipping_fax = forms.CharField(label = ugettext_lazy('Fax'), required=False)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-addresses-edit'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('addresses-route')
        self.helper.layout = Layout(
            Fieldset(
                ugettext_lazy("Rechnungsadresse"),
                'billing_street',
                'billing_city',
                'billing_zip',
                'billing_country',
                'billing_language',
                'billing_tel',
                'billing_mobile',
                'billing_fax'
            ), Fieldset(
                ugettext_lazy("Lieferadresse"),
                'shipping_street',
                'shipping_city',
                'shipping_zip',
                'shipping_country',
                'shipping_language',
                'shipping_tel',
                'shipping_mobile',
                'shipping_fax'
            ), FormActions(
                Submit('submit', ugettext_lazy('Speichern'), css_class='btn btn-primary')
            )
        )
        super(AddressesForm, self).__init__(*args, **kwargs)