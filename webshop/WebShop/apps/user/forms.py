from django import forms
from django.forms import widgets, ValidationError
from django.forms.util import ErrorList
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.urlresolvers import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML, Fieldset, Hidden
from crispy_forms.bootstrap import FormActions



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



class LoginEmailForm(forms.Form):
    email = forms.EmailField(label = ugettext_lazy('E-mail Address'))
    password = forms.CharField(widget = forms.PasswordInput, label = ugettext_lazy('Password'))
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-email-login'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('WebShop.apps.user.views.auth.login')
        self.helper.layout = Layout(
            Fieldset(
                ugettext_lazy("Login with email and password"),
                'email',
                'password'
            ),
            FormActions(
                Submit('submit', ugettext_lazy('Login'), css_class='btn btn-primary')
            )
        )
        super(LoginEmailForm, self).__init__(*args, **kwargs)

class LoginZipCodeForm(forms.Form):
    username = forms.CharField(label = ugettext_lazy('Kundennummer'))
    password = forms.CharField(widget = forms.PasswordInput, label = ugettext_lazy('PLZ'))
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-zipcode-login'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('WebShop.apps.user.views.auth.login_zipcode')
        self.helper.layout = Layout(
            Fieldset(
                ugettext_lazy("Login with customer number and ZIP code"),
                'username',
                'password'
            ),
            HTML("<p>{}</p>".format(_("Please observe that customer number and ZIP code only work, if you have received that Login by mail."))
#                    <p>Bitte beachten Sie, das Kundennummer und PLZ einloggen nur klappt, wenn Sie die Information auch per Post erhalten haben.</p>
            ),
            FormActions(
                Submit('submit', ugettext_lazy('Login'), css_class='btn btn-primary')
            )
        )
        super(LoginZipCodeForm, self).__init__(*args, **kwargs)


class RequestPasswordForm(forms.Form):
    email = forms.EmailField(label = ugettext_lazy('Email Address'))
    emailconfirm = forms.EmailField(label = ugettext_lazy('Retype Email Address'))
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-forgot-password-form'
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('WebShop.apps.user.views.auth.forgot_password')
        self.helper.layout = Layout(
            Fieldset(
                ugettext_lazy('Change Password'),
                'email',
                'emailconfirm'
            ),
            FormActions(
                Submit('submit', ugettext_lazy("Send Email"), css_class='btn btn-primary')
            )
        )
        super(RequestPasswordForm, self).__init__(*args, **kwargs)
    def clean_emailconfirm(self):
        if self.data['email'] != self.data['emailconfirm']:
            raise ValidationError(_('Sorry, your email addresses do not match.'))
        return self.data['email']

class RegisterForm(forms.Form):
    role = forms.ChoiceField(choices = [('K', _('Studio')), ('E', _('Endkunde'))], widget=forms.Select
                             , label = ugettext_lazy('Ich bin'))
    email = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)
    password2 = forms.CharField(widget = forms.PasswordInput)

    def clean_email(self):
        if(User.objects.filter(email=self.data['email']).count()):
            raise ValidationError(mark_safe(_('Your email address has been registered.')))
        else:
            return self.data['email']
        
    def clean_password2(self):
        if self.data['password'] != self.data['password2']:
            raise ValidationError(mark_safe(_('Sorry, please check your password.')))
        return self.data['password2']

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_id = 'id-signup-form'
        self.helper.form_class = 'form-horizontal form-validated'
        self.helper.form_method = 'post'
        self.helper.form_action = reverse('WebShop.apps.user.views.auth.signup')
        self.helper.layout = Layout(
            Fieldset(
                ugettext_lazy('Signup'),
                'role',
                'email',
                'password',
                'password2'
            ),
            FormActions(
                Submit('submit', ugettext_lazy("Signup"), css_class='btn btn-primary')
            )
        )
        super(RegisterForm, self).__init__(*args, **kwargs)











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
