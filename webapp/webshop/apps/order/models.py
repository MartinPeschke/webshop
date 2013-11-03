from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from webshop.utils.jsonfield import JSONField

__author__ = 'Martin'

class PaymentMethodManager(models.Manager):
    def filter_by_role(self, role):
        return PaymentMethod.objects.filter(least_role__lte = role)


class PaymentMethod(models.Model):
    class Meta:
        db_table = 'apps_payment_method'
    objects = PaymentMethodManager()

    name = models.CharField(unique=True, max_length=64)
    least_role = models.CharField(max_length=1)

    LABEL_MAP = {
        'CASH' : _("PAYMENT_METHOD_CASH"),
        'CASH_ON_DELIVERY':_("PAYMENT_METHOD_CASH_ON_DELIVERY"),
        'BANK_TRANSFER':_("PAYMENT_METHOD_BANK_TRANSFER"),
        'CREDITCARD':_("PAYMENT_METHOD_CREDITCARD"),
        'DIRECT_DEBIT':_("PAYMENT_METHOD_DIRECT_DEBIT"),
        'PAYPAL': _("PAYMENT_METHOD_PAYPAL"),
        'INVOICE': _("PAYMENT_METHOD_INVOICE")
    }
    def get_html_label(self):
        return mark_safe(u'<span class="">{}</span>'.format(self.__unicode__()))
    def __unicode__(self):
        return unicode(self.LABEL_MAP.get(self.name, self.name))




class OrderStatus(models.Model):
    class Meta:
        db_table = 'apps_order_status'
    name = models.CharField(unique=True, max_length=64)
    LABEL_MAP = {
        'ERROR' : ("important", _("ORDER_STATUS_ERROR")),
        'DELETED':("inverse", _("ORDER_STATUS_DELETED")),
        'CURRENT':("info", _("ORDER_STATUS_CURRENT")),
        'ORDERED':("warning", _("ORDER_STATUS_ORDERED")),
        'SUBMITTED_TO_BACKEND':("success", _("ORDER_STATUS_SUBMITTED_TO_BACKEND")),
        }
    def get_html_label(self):
        return mark_safe(u'<span class="label label-{}">{}</span>'.format(*self.LABEL_MAP[self.name]))
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
    ordered_in_shop = models.CharField(null=True, blank = True, default = settings.SHOP_NAME, max_length=255)
    #alter table devel.apps_order add column meta_data text;
    meta_data = JSONField(null=True, blank=True)

    def __unicode__(self):
        return u'<Order:{}  Status: {}>'.format(self.id, self.status.name)

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
    def get_display_ref(self):
        if self.ao_ref and self.ao_ref != '-':
            return "{}-{}".format(self.a_ref, self.ao_ref)
        else:
            return self.a_ref
    def __unicode__(self):
        return u'%s: %spcs' % (self.get_display_ref(), self.qty)

    class Meta:
        db_table = 'apps_orderitem'



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
        return self.owner
    def __unicode__(self):
        return self.owner
    class Meta:
        db_table = 'apps_bankaccount'




class CreditCardType(models.Model):
    class Meta:
        db_table = 'apps_creditcard_type'
    name = models.TextField(unique=True, max_length = 32)
    LABEL_MAP = {
        'VISA' : _("CREDITCARD_VISA"),
        'MASTERCARD':_("CREDITCARD_MASTERCARD"),
        }
    def get_html_label(self):
        return mark_safe('<span class="">{}</span>'.format(*self.LABEL_MAP[self.name]))
    def __unicode__(self):
        return unicode(self.LABEL_MAP.get(self.name, self.name))


class CreditCard(models.Model):
    owner = models.CharField(max_length=128)
    cardno = models.CharField(max_length=64) # private

    valid_until = models.CharField(max_length=10)    #models.DateTimeField()
    security_number = models.CharField(max_length=16) # new since update, need import

    user = models.ForeignKey(User)
    cctype = models.ForeignKey(CreditCardType)

    def setCCNumber(self, value):
        self.cardno = value
    def getCCNumber(self):
        return '%s%s' % ('x'*12,self.cardno[-4:])
    ccNumber = property(getCCNumber, setCCNumber)
    def __repr__(self):
        return u'%s' % self.cardno

    class Meta:
        db_table = 'apps_creditcard'
