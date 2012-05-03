from django.utils.safestring import mark_safe

__author__ = 'Martin'
from django import forms
from django.conf import settings



class PaymentFormWholesale(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PaymentFormWholesale, self).__init__(*args, **kwargs)
        self.fields['payment_method'].choices = []
        for key, value in settings.PAYMENT_METHODS:
            self.fields['payment_method'].choices.append((key, mark_safe(_(value))))

    payment_method = forms.ChoiceField(widget=forms.RadioSelect, choices=())
    payment_comment = forms.Textarea()

class PaymentFormRetail(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PaymentFormRetail, self).__init__(*args, **kwargs)
        self.fields['payment_method'].choices = []
        for key, value in settings.PAYMENT_METHODS[:-2]:
            self.fields['payment_method'].choices.append((key, mark_safe(_(value))))

    payment_method = forms.ChoiceField(widget=forms.RadioSelect, choices=())
    payment_comment = forms.Textarea()

class CreditCardForm(forms.Form):
    owner = forms.CharField()
    ccNumber = forms.CharField()
    ctype = forms.ChoiceField(choices=settings.CARD_ROLES)
    valid_until = forms.CharField()    #models.DateTimeField()
    security_number = forms.CharField() # new since update, need import

class BankAccountForm(forms.Form):
    owner = forms.CharField()
    accountno = forms.CharField()
    blz = forms.CharField()
    bank_name = forms.CharField()    #models.DateTimeField()
