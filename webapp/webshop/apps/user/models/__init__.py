from django.core.exceptions import ObjectDoesNotExist
from webshop.apps.order.models import PaymentMethod
from webshop.utils.jsonfield import JSONField
import json
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from webshop.apps.contrib.decorator import json_encode
from webshop.apps.user.user_roles import USER_GROUPS, userRoles, NORM_ROLE


__author__ = 'Martin'


from webshop.apps.order.models import BankAccount, CreditCard
from .password_token import PasswordToken,RESETPASSWORDTOKEN, REGISTERNEWTOKEN, APPROVALWHOLESALETOKEN
from .address import Address, Language, AddressType




class Profile(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    # Name
    title = models.CharField(max_length=8, choices=settings.TITLE_CHOICES)
    first_name = models.CharField(max_length=32, blank=True)
    last_name = models.CharField(max_length=32, blank=True)

    # Company
    company_name = models.CharField(max_length=128, blank=True)
    vat_id = models.CharField(max_length=64, blank=True)
    taxFreed = models.BooleanField(default=False)
    opening_hours = models.CharField(max_length=32, blank=True)
    bo_customer_no = models.CharField(max_length=64, blank=True)

    webpage = models.CharField(max_length=255, blank=True)

    same_address = models.NullBooleanField(null=True)
    role = models.CharField(max_length=1, choices=USER_GROUPS)
    weekdays = JSONField(blank=True)

    preferred_payment_method = models.ForeignKey(PaymentMethod)
    user = models.ForeignKey(User)

    def _getRoleName(self):
        return _(userRoles[self.role])
    roleName = property(_getRoleName)


    def _serialize(self):
        try:
            account = BankAccount.objects.get(user = self.user)
        except:
            account = {}
        try:
            creditcard = CreditCard.objects.get(user = self.user)
        except:
            creditcard= {}

        return json_encode({'bo_customer_no':   self.bo_customer_no,
                            'exists':  self and True or False,
                            'login':   self and self.user.email or None,
                            'user':    self.user,
                            'profile': self,
                            'addresses': self.user.address_set.all(),
                            'bankaccount':account,
                            'creditcard':creditcard})

    def _deserialize(self, data):
        data = json.loads(data)

        webuser = data['webuser']
        self.user.email = webuser['email']
        pw = webuser['password']
        if(pw[:5] != 'sha1$'):
            self.user.set_password(pw)
        self.user.save()

        profile = data['profile']
        for k,v in profile.iteritems():
            setattr(self, k, v)
        self.save()

        shipping = self.user.address_set.get(type='shipping')
        for k,v in data['shipping'].iteritems():
            setattr(shipping, k, v)
        shipping.save()

        billing = self.user.address_set.get(type='billing')
        for k,v in data['billing'].iteritems():
            setattr(billing, k, v)
        billing.save()

    json = property(_serialize, _deserialize)

    def json_equivalent(self):
        dictionary = {}
        for field in self._meta.get_all_field_names():
            try:
                dictionary[field] = self.__getattribute__(field)
            except ObjectDoesNotExist:
                pass
        return dictionary

    def get_pretty_name(self):
        return " ".join([self.first_name, self.last_name])

    def __repr__(self):
        return '<Profile: %s>' % self.company_name

    class Meta:
        db_table = 'apps_profile'

