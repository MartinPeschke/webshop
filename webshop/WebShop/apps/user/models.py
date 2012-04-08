# -*- coding : utf-8 -*-
from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

import simplejson

from WebShop.apps.contrib.decorator import json_encode
from WebShop.utils.etl import USER_GROUPS, userRoles, NO_RIGHTS, HAS_RIGHTS
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.safestring import mark_safe
from django.conf import settings

RESETPASSWORDTOKEN = 1
REGISTERNEWTOKEN = 2
APPROVALWHOLESALETOKEN = 3

ADDRESS_TYPES = (
    ('billing', mark_safe(_('Billing Address'))),
    ('shipping', mark_safe(_('Shipping Address'))),
)


class CreditCard(models.Model):

    owner = models.CharField(max_length=128)
    
    cardno = models.CharField(max_length=64) # private
    
    def setCCNumber(self, value):
        self.cardno = value

    def getCCNumber(self):
        return '%s%s' % ('x'*16,self.cardno[-4:])

    ccNumber = property(getCCNumber, setCCNumber)
    
    ctype = models.CharField(max_length=64, choices=settings.CARD_ROLES)
    valid_until = models.CharField(max_length=10)    #models.DateTimeField()
    security_number = models.CharField(max_length=16) # new since update, need import 

    user = models.ForeignKey(User)
    
    def __repr__(self):
        return u'%s' % self.cardno
    
    class Meta:
        db_table = 'apps_creditcard'

        
class BankAccount(models.Model): # no change for import, if IDs are same

    # Properties
    bank_name = models.CharField(max_length=255)
    owner = models.CharField(max_length=128)
    blz = models.CharField(max_length=255, blank=True)
    iban = models.CharField(max_length=255, blank=True)
    swift = models.CharField(max_length=255, blank=True)
    accountno = models.CharField(max_length=255)

    # Relationship
    user = models.ForeignKey(User)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'apps_bankaccount'

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
    payment_method = models.CharField(max_length=32, choices=settings.PAYMENT_METHODS, blank=True)
    
    same_address = models.NullBooleanField(null=True)
    role = models.CharField(max_length=1, choices=USER_GROUPS)
    weekdays = models.CharField(max_length=128, blank=True)
    
#    def _getNiceWeekDayStr(self):
#        return ', '.join(simplejson.loads(self.weekdays))
#    niceWeekDayStr = property(_getNiceWeekDayStr)

    # Relationship
    user = models.ForeignKey(User)

    def get_payment_method(self):
        return dict(settings.PAYMENT_METHODS).get(self.payment_method, 'Unknown')
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
        data = simplejson.loads(data)
        
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
    
    def __repr__(self):
        return '<Profile: %s>' % self.company_name
    
    class Meta:
        db_table = 'apps_profile'
        
        
        

class Address(models.Model):    
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=64)
    zip = models.CharField(max_length=16)
    country = models.CharField(max_length=32)
    language = models.CharField(max_length=32)
    tel = models.CharField(max_length=32)
    mobile = models.CharField(max_length=32, blank=True)
    fax = models.CharField(max_length=32, blank=True)
    
    type = models.CharField(max_length=32, choices=ADDRESS_TYPES) # Billing, Shipping+
    
    # Relationship
    user = models.ForeignKey(User)
    
    def __str__(self):
        return "<Address %s for %s>" %(self.type, self.user_id)
    
    class Meta:
        db_table = 'apps_address'

    class Admin:
        list_display = ('user', 'type', 'country', 'city')

class PasswordToken(models.Model):

    role = models.IntegerField(default=RESETPASSWORDTOKEN)
    value = models.CharField(max_length=64) # NO MULTICOL UNIQUE POSSIBLE :(
    create_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    
    def __str__(self):
        return self.value

    class Meta:
        db_table = 'apps_passwdtoken'
    
    class Admin:
        pass