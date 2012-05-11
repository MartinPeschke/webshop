from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from WebShop.utils.jsonfield import JSONField
from django.utils.translation import ugettext as _

class OrderStatus(models.Model):
    name = models.TextField(unique=True)
    LABEL_MAP = {
        'ERROR' : ("important", _("ORDER_STATUS_ERROR")),
        'DELETED':("inverse", _("ORDER_STATUS_DELETED")),
        'CURRENT':("info", _("ORDER_STATUS_CURRENT")),
        'ORDERED':("warning", _("ORDER_STATUS_ORDERED")),
        'SUBMITTED_TO_BACKEND':("success", _("ORDER_STATUS_SUBMITTED_TO_BACKEND")),
        }
    class Meta:
        db_table = 'apps_order_status'
    def get_html_label(self):
        return mark_safe('<span class="label label-{}">{}</span>'.format(*self.LABEL_MAP[self.name]))

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
    status = models.ForeignKey(OrderStatus)

    user = models.ForeignKey(User)

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

