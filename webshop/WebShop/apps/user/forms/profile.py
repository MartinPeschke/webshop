__author__ = 'Martin'
from django import forms
from django.forms.widgets import Select
from django.utils.translation import ugettext, ugettext_lazy
from operator import attrgetter

from WebShop.apps.user.models.address import Language
from WebShop.apps.lib.baseviews import BaseForm, Fieldset
from WebShop.apps.contrib.countries.models import Country

COUNTRIES = map(attrgetter('iso', 'printable_name'), Country.objects.all())
LANGUAGES = map(attrgetter('code', 'name'), Language.objects.all())

class AddressesForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext("Rechnungsadresse"),
                'billing_street',
                'billing_city',
                'billing_zip',
                'billing_country',
                'billing_language',
                'billing_tel',
                'billing_mobile',
                'billing_fax'
            ), Fieldset(
                ugettext("Lieferadresse"),
                'shipping_street',
                'shipping_city',
                'shipping_zip',
                'shipping_country',
                'shipping_language',
                'shipping_tel',
                'shipping_mobile',
                'shipping_fax'
            )
        )

    billing_street = forms.CharField(label = ugettext_lazy('Strasse'), required=True)
    billing_city = forms.CharField(label = ugettext_lazy('Stadt'), required=True)
    billing_zip = forms.CharField(label = ugettext_lazy('PLZ'), required=True)
    billing_country = forms.ChoiceField(choices=COUNTRIES, widget=Select, label = ugettext_lazy('Land'), required=True)
    billing_language = forms.ChoiceField(choices=LANGUAGES, widget=Select, label = ugettext_lazy('Bevorzugte Sprache'), required=True)
    billing_tel = forms.CharField(label = ugettext_lazy('Telefon'), required=True)
    billing_mobile = forms.CharField(label = ugettext_lazy('Mobil'), required=False)
    billing_fax = forms.CharField(label = ugettext_lazy('Fax'), required=False)

    shipping_street = forms.CharField(label = ugettext_lazy('Strasse'), required=True)
    shipping_city = forms.CharField(label = ugettext_lazy('Stadt'), required=True)
    shipping_zip = forms.CharField(label = ugettext_lazy('PLZ'), required=True)
    shipping_country = forms.ChoiceField(choices=COUNTRIES, widget=Select, label = ugettext_lazy('Land'), required=True)
    shipping_language = forms.ChoiceField(choices=LANGUAGES, widget=Select, label = ugettext_lazy('Bevorzugte Sprache'), required=True)
    shipping_tel = forms.CharField(label = ugettext_lazy('Telefon'), required=True)
    shipping_mobile = forms.CharField(label = ugettext_lazy('Mobil'), required=False)
    shipping_fax = forms.CharField(label = ugettext_lazy('Fax'), required=False)
