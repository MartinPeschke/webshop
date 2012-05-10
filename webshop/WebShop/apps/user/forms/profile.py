__author__ = 'Martin'
from operator import itemgetter, attrgetter
from django import forms
from django.conf import settings
from django.forms.widgets import Select
from django.utils.translation import ugettext, ugettext_lazy
from django.utils.translation import ugettext as _, ugettext_lazy
from WebShop.apps.lib.baseviews import BaseForm, Fieldset


from .auth import WEEKDAYS, COUNTRIES, LANGUAGES

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

    billing_street = forms.CharField(label = ugettext_lazy('Strasse*'), required=True)
    billing_city = forms.CharField(label = ugettext_lazy('Stadt*'), required=True)
    billing_zip = forms.CharField(label = ugettext_lazy('PLZ*'), required=True)
    billing_country = forms.ChoiceField(choices=COUNTRIES, widget=Select, label = ugettext_lazy('Land'), required=True)
    billing_language = forms.ChoiceField(choices=LANGUAGES, widget=Select, label = ugettext_lazy('Bevorzugte Sprache'), required=True)
    billing_tel = forms.CharField(label = ugettext_lazy('Telefon*'), required=True)
    billing_mobile = forms.CharField(label = ugettext_lazy('Mobil'), required=False)
    billing_fax = forms.CharField(label = ugettext_lazy('Fax'), required=False)

    shipping_street = forms.CharField(label = ugettext_lazy('Strasse*'), required=True)
    shipping_city = forms.CharField(label = ugettext_lazy('Stadt*'), required=True)
    shipping_zip = forms.CharField(label = ugettext_lazy('PLZ*'), required=True)
    shipping_country = forms.ChoiceField(choices=COUNTRIES, widget=Select, label = ugettext_lazy('Land'), required=True)
    shipping_language = forms.ChoiceField(choices=LANGUAGES, widget=Select, label = ugettext_lazy('Bevorzugte Sprache'), required=True)
    shipping_tel = forms.CharField(label = ugettext_lazy('Telefon'), required=False)
    shipping_mobile = forms.CharField(label = ugettext_lazy('Mobil'), required=False)
    shipping_fax = forms.CharField(label = ugettext_lazy('Fax'), required=False)



class AccountRetailDetailsForm(BaseForm):
    title = forms.ChoiceField(choices=settings.TITLE_CHOICES, label = ugettext_lazy('Anrede'))
    first_name = forms.CharField(max_length = 32, label = ugettext_lazy('Vorname*'))
    last_name = forms.CharField(max_length = 32, label = ugettext_lazy('Nachname*'))
    class Meta:
        layout = (
            Fieldset(
                _('Registrierung'),
                'title',
                'first_name',
                'last_name'
            ),
            )

class AccountWholesaleDetailsForm(AccountRetailDetailsForm):
    webpage = forms.CharField(required=False, label = ugettext_lazy('Webseite'))
    company_name = forms.CharField(label = ugettext_lazy('Studioname*'))
    vat_id = forms.CharField(required=False, label = ugettext_lazy('Umsatzsteuer ID'))
    bo_customer_no = forms.CharField(required=False, label = ugettext_lazy('Kundennummer'))
    opening_hours = forms.CharField(label = ugettext_lazy(u'&Ouml;ffnungszeiten*'))
    weekdays = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple
        ,choices=WEEKDAYS
        ,label = ugettext_lazy(u'Wochentage'))
    class Meta:
        layout = (
            Fieldset(
                _('Registrierung'),
                'company_name',
                'title',
                'first_name',
                'last_name',
                'webpage',

                'bo_customer_no',
                'opening_hours',
                'weekdays',
                'vat_id',
            ),
            )
