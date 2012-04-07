from django import forms
from django.forms import widgets, ValidationError
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.safestring import mark_safe
from django.conf import settings



LANGUAGES = []
for key, value in settings.LANGUAGES:
    LANGUAGES.append((key, mark_safe(_(value))))

WEEKDAYS = (
    ('Mon', mark_safe(ugettext_lazy('Monday'))),
    ('Tue', mark_safe(ugettext_lazy('Tuesday'))),
    ('Wed', mark_safe(ugettext_lazy('Wednesday'))),
    ('Thu', mark_safe(ugettext_lazy('Thursday'))),
    ('Fri', mark_safe(ugettext_lazy('Friday'))),
    ('Sat', mark_safe(ugettext_lazy('Saturday'))),
)

YESNO = (('Y', ugettext_lazy('Yes')), (('N'), ugettext_lazy('No')))

class RegisterForm(forms.Form):
    '''
    Form for register
    '''
    email = forms.CharField()
    password = forms.CharField()
    password2 = forms.CharField()
#    use_ssl = forms.BooleanField()

    def clean_email(self):
        if(User.objects.filter(email=self.data['email']).count()):
            raise ValidationError(mark_safe(_('Your email address has been registered.')))
        else:
            return self.data['email']
        
    def clean_password2(self):
        if self.data['password'] != self.data['password2']:
            raise ValidationError(mark_safe(_('Sorry, please check your password.')))
        return self.data['password2']


class AddressForm(forms.Form):
    '''
    Form for Billing Information
    '''
    street = forms.CharField()
    city = forms.CharField()
    zip = forms.CharField(max_length=16)
    country = forms.CharField(max_length=32)
    language = forms.ChoiceField(choices=LANGUAGES)
    tel = forms.CharField(max_length=32)
    mobile = forms.CharField(required=False, max_length=32)
    fax = forms.CharField(required=False, max_length=32)

class ShippingForm(AddressForm):
    '''
    Form for Billing Information
    '''
    street = forms.CharField(required=False)
    city = forms.CharField(required=False)
    zip = forms.CharField(required=False, max_length=16)
    country = forms.CharField(required=False, max_length=32)
    language = forms.ChoiceField(required=False, choices=LANGUAGES)
    tel = forms.CharField(required=False, max_length=32)
    mobile = forms.CharField(required=False, max_length=32)
    fax = forms.CharField(required=False, max_length=32)

class AccountForm(forms.Form):
    # Profile
    
    title = forms.ChoiceField(choices=settings.TITLE_CHOICES)
    first_name = forms.CharField(max_length = 32)
    last_name = forms.CharField(max_length = 32)
    webpage = forms.CharField(required=False)

    company_name = forms.CharField()
    vat_id = forms.CharField(required=False)
    bo_customer_no = forms.CharField(required=False)
    opening_hours = forms.CharField()

    weekdays = forms.CharField(widget=widgets.CheckboxSelectMultiple(choices=WEEKDAYS))
    same_address = forms.CharField(widget=widgets.RadioSelect(choices=YESNO), required=False)
    agree = forms.CharField(widget=widgets.RadioSelect(choices=YESNO))

    def clean_agree(self):
        if(self.data['agree']!=u'Y'):
            raise ValidationError(mark_safe(_('Nur nach Zustimmung zu unseren AGB koennen Sie sich registrieren')))
        else:
            return self.data['agree']
    

class ChangePasswordForm(forms.Form):
    
    password = forms.CharField(widget=widgets.PasswordInput)
    password2 = forms.CharField(widget=widgets.PasswordInput)
        
    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise ValidationError(_('Sorry, please check your password.'))
        return self.data['password']
    
class RequestPasswordForm(forms.Form):
    
    email = forms.EmailField()
    emailconfirm = forms.EmailField()
        
    def clean_emailconfirm(self):
        if self.data['email'] != self.data['emailconfirm']:
            raise ValidationError(_('Sorry, your email addresses do not match.'))
        return self.data['email']    

class OrderFreeCatalogForm(forms.Form):
    
    title = forms.ChoiceField(choices=settings.TITLE_CHOICES)
    first_name = forms.CharField()
    last_name = forms.CharField()
    company_name = forms.CharField(required=False)
    
    street = forms.CharField()
    city = forms.CharField()
    zip = forms.CharField()
    country = forms.CharField()

    email = forms.EmailField()
    tel = forms.CharField()
    fax = forms.CharField(required=False)

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
