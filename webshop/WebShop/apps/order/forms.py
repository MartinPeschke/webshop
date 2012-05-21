from WebShop.apps.lib.validators import ValidateDigits, CreditCardExpiryField, CreditCardNumberField

__author__ = 'Martin'
from bootstrap.forms import Fieldset
from django.forms.widgets import RadioSelect, Textarea, TextInput
from django.utils.translation import ugettext as _, ugettext_lazy
from WebShop.apps.lib.baseviews import BaseForm
from WebShop.apps.order.models import PaymentMethod, CreditCardType, BankAccount, CreditCard

from django import forms
from django.conf import settings


class PaymentMethodForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy("Zahlweise angeben"),
                'payment_method',
                'payment_comment'
            ),
            )
    payment_method = forms.ModelChoiceField(queryset=PaymentMethod.objects.all()
        , widget = RadioSelect(attrs={"class":"paymentmethod"})
        , required=True
        , empty_label=None
        , label = ugettext_lazy("Zahlart")
    )
    payment_comment = forms.CharField(widget = Textarea(attrs={"class":"span5"})
        , label = ugettext_lazy("Bestellkommentar")
        , required = False
    )
    def __init__(self, role, *args, **kwargs):
        super(PaymentMethodForm, self).__init__(*args, **kwargs)
        self.fields['payment_method'].queryset =\
        PaymentMethod.objects.filter_by_role(role)





class CreditCardNumber(forms.CharField):
    def to_python(self, value):
        value = value.replace(" ", "")
        return value

class CreditCardForm(BaseForm, ):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy("Kreditkartendetails"),
                'owner',
                'ccNumber',
                'cctype',
                'valid_until',
                'security_number'
            ),
            )
    owner = forms.CharField(label=ugettext_lazy("Karteninhaber*"), widget = TextInput(attrs={"class":"required"}))
    ccNumber = CreditCardNumber(label=ugettext_lazy("Kartennummer*"), widget = TextInput(attrs={"class":"required"}), min_length=15)
    cctype = forms.ModelChoiceField(queryset=CreditCardType.objects.all(), label=ugettext_lazy("Typ"), empty_label=None)
    valid_until = CreditCardExpiryField(label=ugettext_lazy("G&uuml;ltig bis*"), widget = TextInput(attrs={"class":"required"}), help_text=ugettext_lazy("Beispiel: 10/2015"))
    security_number = forms.CharField(label=ugettext_lazy("Sicherheitscode*"), widget = TextInput(attrs={"class":"required"}), max_length=3)
    def __init__(self, user = None, *args, **kwargs):
        if user is not None:
            try:
                cc = CreditCard.objects.get(user=user)
            except CreditCard.DoesNotExist:
                initial = {}
            else:
                initial = {'owner' : cc.owner, 'ccNumber':cc.ccNumber, 'cctype':cc.cctype, 'valid_until':cc.valid_until, 'security_number':cc.security_number}
            kwargs['initial'] = initial
        kwargs['prefix'] = 'creditcard'
        super(CreditCardForm, self).__init__(*args, **kwargs)

    def save(self, user):
        card, created = CreditCard.objects.get_or_create(user=user, cctype = self.cleaned_data['cctype'])
        for k,v in self.cleaned_data.items():
            setattr(card, k,v)
        card.save()



class BankAccountForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy("Kontodaten"),
                'owner',
                'accountno',
                'blz',
                'bank_name'
            ),
            )
    owner = forms.CharField(label=ugettext_lazy("Kontoinhaber*"), widget = TextInput(attrs={"class":"required"}))
    accountno = forms.CharField(label=ugettext_lazy("Kontonummer*"), widget = TextInput(attrs={"class":"required"}))
    blz = forms.CharField(label=ugettext_lazy("BLZ*"), widget = TextInput(attrs={"class":"required"}))
    bank_name = forms.CharField(label=ugettext_lazy("Bank*"), widget = TextInput(attrs={"class":"required"}))
    def __init__(self, user = None, *args, **kwargs):
        if user is not None:
            try:
                account = BankAccount.objects.get(user=user)
            except BankAccount.DoesNotExist:
                initial = {}
            else:
                initial = {'owner' : account.owner, 'accountno':account.accountno, 'blz':account.blz, 'bank_name':account.bank_name}
            kwargs['initial'] = initial
        kwargs['prefix'] = 'account'
        super(BankAccountForm, self).__init__(*args, **kwargs)

    def save(self, user):
        account, created  = BankAccount.objects.get_or_create(user=user)
        for k,v in self.cleaned_data.items():
            setattr(account, k,v)
        account.save()