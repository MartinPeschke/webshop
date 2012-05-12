from bootstrap.forms import Fieldset
from django.forms.widgets import RadioSelect, Textarea
from django.utils.translation import ugettext as _, ugettext_lazy
from WebShop.apps.lib.baseviews import BaseForm
from WebShop.apps.user.models.creditcard import CreditCardType
from WebShop.apps.user.models import PaymentMethod

__author__ = 'Martin'
from django import forms
from django.conf import settings


class PaymentMethodForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                _("Zahlweise angeben"),
                'payment_method',
                'payment_comment'
            ),
        )
    payment_method = forms.ModelChoiceField(queryset=PaymentMethod.objects.all()
            , widget = RadioSelect
            , required=True
            , empty_label=None
            , label = ugettext_lazy("Zahlart")
        )
    payment_comment = forms.CharField(widget = Textarea(attrs={"class":"span5"})
            , label = ugettext_lazy("Bestellkommentar")
        )
    def __init__(self, role, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        self.fields['payment_method'].queryset =\
            PaymentMethod.objects.filter(least_role__lt = role)


class CreditCardForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                _("Kreditkartendetails"),
                'owner',
                'ccNumber',
                'cctype',
                'valid_until',
                'security_number'
            ),
        )
    owner = forms.CharField(label=ugettext_lazy("Karteninhaber"))
    ccNumber = forms.CharField(label=ugettext_lazy("Kartennummer"))
    cctype = forms.ModelChoiceField(queryset=CreditCardType.objects.all(), label=ugettext_lazy("Typ"))
    valid_until = forms.CharField(label=ugettext_lazy("G&uuml;ltig bis"))
    security_number = forms.CharField(label=ugettext_lazy("Sicherheitscode"))

class BankAccountForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                _("Kontodaten"),
                'owner',
                'accountno',
                'blz',
                'bank_name'
            ),
        )
    owner = forms.CharField(label=ugettext_lazy("Kontoinhaber"))
    accountno = forms.CharField(label=ugettext_lazy("Kontonummer"))
    blz = forms.CharField(label=ugettext_lazy("BLZ"))
    bank_name = forms.CharField(label=ugettext_lazy("Bank"))
