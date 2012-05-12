from django.core.exceptions import ObjectDoesNotExist
from WebShop.utils.jsonfield import JSONField
import simplejson
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from WebShop.apps.contrib.decorator import json_encode
from WebShop.apps.user.user_roles import USER_GROUPS, userRoles, NORM_ROLE


__author__ = 'Martin'


from .bank_account import BankAccount
from .creditcard import CreditCard
from .password_token import PasswordToken,RESETPASSWORDTOKEN, REGISTERNEWTOKEN, APPROVALWHOLESALETOKEN
from .address import Address, Language, AddressType


class PaymentMethod(models.Model):
    class Meta:
        db_table = 'apps_payment_method'
    name = models.TextField(unique=True)
    least_role = models.CharField(max_length=1)

    LABEL_MAP = {
        'CASH' : _("PAYMENT_METHOD_CASH"),
        'CASH_ON_DELIVERY':_("PAYMENT_METHOD_CASH_ON_DELIVERY"),
        'BANK_TRANSFER':_("PAYMENT_METHOD_BANK_TRANSFER"),
        'CREDITCARD':_("PAYMENT_METHOD_CREDITCARD"),
        'DIRECT_DEBIT':_("PAYMENT_METHOD_DIRECT_DEBIT"),
        'PAYPAL': _("PAYMENT_METHOD_PAYPAL")
    }
    def get_html_label(self):
        return mark_safe('<span class="">{}</span>'.format(self.__unicode__()))
    def __unicode__(self):
        return unicode(self.LABEL_MAP.get(self.name, self.name))


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

    def json_equivalent(self):
        dictionary = {}
        for field in self._meta.get_all_field_names():
            try:
                dictionary[field] = self.__getattribute__(field)
            except ObjectDoesNotExist:
                pass
        return dictionary


    def __repr__(self):
        return '<Profile: %s>' % self.company_name

    class Meta:
        db_table = 'apps_profile'



class OrderStatus(models.Model):
    class Meta:
        db_table = 'apps_order_status'
    name = models.TextField(unique=True)
    LABEL_MAP = {
        'ERROR' : ("important", _("ORDER_STATUS_ERROR")),
        'DELETED':("inverse", _("ORDER_STATUS_DELETED")),
        'CURRENT':("info", _("ORDER_STATUS_CURRENT")),
        'ORDERED':("warning", _("ORDER_STATUS_ORDERED")),
        'SUBMITTED_TO_BACKEND':("success", _("ORDER_STATUS_SUBMITTED_TO_BACKEND")),
        }
    def get_html_label(self):
        return mark_safe('<span class="label label-{}">{}</span>'.format(*self.LABEL_MAP[self.name]))
    def __unicode__(self):
        return self.LABEL_MAP.get(self.name, self.name)

class Order(models.Model):
    '''
    When user have confirmed his shopping data, an order will be created.
    Order can never be changed, so I store it into XML format.
    '''
    #===============================================================================
    # -2 - Error in Sending EMail
    # -1 - deleted
    #  0 - current shopping list
    #  1 - ordered
    #  2 - synched to BOP
    #===============================================================================
    user = models.ForeignKey(User)
    status = models.ForeignKey(OrderStatus)
    payment_method = models.ForeignKey(PaymentMethod)

    comment = models.TextField(null=True, blank = True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    ordered_in_shop = models.TextField(null=True, blank = True, default = settings.SHOP_NAME)
    #alter table devel.apps_order add column meta_data text;
    meta_data = JSONField(null=True, blank=True)

    def __unicode__(self):
        return u'<Order:%s, Status: %s>' % (self.id, self.status)

    class Meta:
        db_table = 'apps_order'

class OrderItem(models.Model):
    '''
    Each ShoppingItem represents a item in Shopping Cart or Saved list.
    Identified by field type.
    '''

    a_ref = models.CharField(max_length=32, db_index=True)
    ao_ref = models.CharField(max_length=16)
    qty = models.IntegerField(default=0)
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discountPrice = models.DecimalField(max_digits=10, decimal_places=2)
    discounted = models.BooleanField(default=False)
    discountQty = models.IntegerField(default=0)
    tax_included = models.BooleanField(default=False)
    description = models.TextField(null = True, blank = True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    #===============================================================================
    # -1 - deleted
    #  0 - current shopping list
    #  1 - ordered
    #===============================================================================
    status = models.IntegerField(default=0)

    # ManyToOne -> ShoppingCart
    order = models.ForeignKey(Order)

    def __unicode__(self):
        return u'%s-%s: %spcs' % (self.a_ref, self.ao_ref, self.qty)

    class Meta:
        db_table = 'apps_orderitem'