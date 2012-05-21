from operator import itemgetter, attrgetter
from django import forms
from django.contrib import auth
from django.forms import widgets, ValidationError
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from WebShop.apps.lib.baseviews import BaseForm, Fieldset
from WebShop.apps.contrib.countries.models import Country
from WebShop.apps.user.models.address import Language
from WebShop.apps.user.user_roles import LEAST_ROLE, AWAITING_APPROVAL_ROLE

COUNTRIES = map(attrgetter('iso', 'printable_name'), Country.objects.all())
LANGUAGES = map(attrgetter('code', 'name'), Language.objects.all())

WEEKDAYS = (
    (u'Mon', mark_safe(ugettext_lazy('Monday'))),
    (u'Tue', mark_safe(ugettext_lazy('Tuesday'))),
    (u'Wed', mark_safe(ugettext_lazy('Wednesday'))),
    (u'Thu', mark_safe(ugettext_lazy('Thursday'))),
    (u'Fri', mark_safe(ugettext_lazy('Friday'))),
    (u'Sat', mark_safe(ugettext_lazy('Saturday'))),
    (u'Sun', mark_safe(ugettext_lazy('Sunday')))
)



YESNO = (('Y', ugettext_lazy('Yes')), (('N'), ugettext_lazy('No')))



class LoginEmailForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy("Mit Email und Passwort anmelden"),
                'email',
                'password'
            ),
        )
    email = forms.EmailField(label = ugettext_lazy('Email'))
    password = forms.CharField(widget = forms.PasswordInput, label = ugettext_lazy('Passwort'))

    def getSubmitLabel(self):
        return _("Anmelden")

    def clean_email(self):
        user = auth.authenticate(email = self.data['email'], password = self.data['password'])
        if user is None:
            raise forms.ValidationError(_('Sorry, please check your email and password.'))
        else:
            self.cleaned_data['user'] = user

class LoginZipCodeForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy("Mit Kundennummer und Postleitzahl anmelden"),
                'username',
                'password'
            ),
        )
    username = forms.CharField(label = ugettext_lazy('Kundennummer'))
    password = forms.CharField(widget = forms.PasswordInput, label = ugettext_lazy('PLZ'), \
        help_text=ugettext_lazy("Anmeldung mit Kundennummer klappt nur, wenn Sie entsprechende Daten per Post von uns erhalten haben."))

    def clean_username(self):
        user = auth.authenticate(**self.cleaned_data)
        if user is None:
            raise forms.ValidationError(_('Sorry, please check your customer number or ZIP code.'))
        elif not user.is_active:
            raise forms.ValidationError(_('Sorry, please activate your account.'))
        else:
            self.cleaned_data['user'] = user
    def getSubmitLabel(self):
        return _("Anmelden")

class RequestPasswordForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy('Passwort &auml;ndern'),
                'email',
            ),
        )
    email = forms.EmailField(label = ugettext_lazy('Email'))
    def getSubmitLabel(self):
        return _("Abschicken")
    def clean_email(self):
        try:
            user = User.objects.get(email = self.data['email'])
        except User.DoesNotExist:
            raise forms.ValidationError(_('Unbekannte Emailadresse.'))
        else:
            self.cleaned_data['user'] = user
            self.cleaned_data['email'] = self.data['email']

class ChangePasswordForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy('Passwort &auml;ndern'),
                'password',
                'password2'
            ),
        )
    password = forms.CharField(widget=widgets.PasswordInput, label = ugettext_lazy('Neues Passwort'))
    password2 = forms.CharField(widget=widgets.PasswordInput, label = ugettext_lazy('Passwort wiederholen'))
        
    def clean_password(self):
        if self.data['password'] != self.data['password2']:
            raise ValidationError(_(u'Passwörter stimmen nicht überein.'))
        return self.data['password']
    def getSubmitLabel(self):
        return _("Speichern")





class RegisterForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy('Registrierung'),
                'role',
                'email',
                'password',
                'password2'
            ),
        )
    role = forms.ChoiceField(choices = [(AWAITING_APPROVAL_ROLE, ugettext_lazy('Studio')), (LEAST_ROLE, ugettext_lazy('Endkunde'))], widget=forms.Select
                             , label = ugettext_lazy('Ich bin'))
    email = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput, label = ugettext_lazy('Passwort'))
    password2 = forms.CharField(widget = forms.PasswordInput, label = ugettext_lazy('Passwort wiederholen'))

    def addRules(self, rules):
        rules['email']['remote'] = reverse('check-email-route')
        rules['email']['email'] = True
        return rules

    def clean_email(self):
        if(User.objects.filter(email=self.data['email']).count()):
            raise ValidationError(mark_safe(_('Diese Emailadresse ist bereits vergeben.')))
        else:
            return self.data['email']
    def clean_password2(self):
        if self.data['password'] != self.data['password2']:
            raise ValidationError(mark_safe(_(u'Bitte überprüfen Sie Ihr Passwort.')))
        return self.data['password2']
    def getSubmitLabel(self):
        return _("Registrieren")

class RetailAccountForm(BaseForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy('Registrierung'),
                'title',
                'first_name',
                'last_name',
                'agree'
            ),
        )

    title = forms.ChoiceField(choices=settings.TITLE_CHOICES, label = ugettext_lazy('Anrede'))
    first_name = forms.CharField(max_length = 32, label = ugettext_lazy('Vorname*'))
    last_name = forms.CharField(max_length = 32, label = ugettext_lazy('Nachname*'))
    agree = forms.ChoiceField(widget=widgets.RadioSelect
        , choices=YESNO
        , initial=YESNO[1][0]
        , label = ugettext_lazy(u'Ich stimme den AGB zu*'))

    def clean_agree(self):
        if(self.data['agree']!=u'Y'):
            raise ValidationError(mark_safe(_(u'Nur nach Zustimmung zu unseren AGB können Sie sich registrieren')))
        else:
            return self.data['agree']
    def getSubmitLabel(self):
        return _("Registrierung abschliessen")


class WholesaleAccountForm(RetailAccountForm):
    class Meta:
        layout = (
            Fieldset(
                ugettext_lazy('Registrierung'),
                'company_name',
                'title',
                'first_name',
                'last_name',
                'webpage',

                'bo_customer_no',
                'opening_hours',
                'weekdays',
                'vat_id',
                'agree'
            ),
        )
    # Profile
    webpage = forms.CharField(required=False, label = ugettext_lazy('Webseite'))
    company_name = forms.CharField(label = ugettext_lazy('Studioname*'))
    vat_id = forms.CharField(required=False, label = ugettext_lazy('Umsatzsteuer ID'))
    bo_customer_no = forms.CharField(required=False, label = ugettext_lazy('Kundennummer'))
    opening_hours = forms.CharField(label = ugettext_lazy(u'Öffnungszeiten*'))

    weekdays = forms.MultipleChoiceField(widget = forms.CheckboxSelectMultiple
                                         ,choices=WEEKDAYS
                                         ,initial=map(itemgetter(0), WEEKDAYS[:5])
                                         ,label = ugettext_lazy(u'Wochentage'))
    def getSubmitLabel(self):
        return _("Registrierung abschliessen")

