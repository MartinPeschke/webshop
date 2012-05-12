from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


__author__ = 'Martin'

class CreditCardType(models.Model):
    class Meta:
        db_table = 'apps_creditcard_type'
    name = models.TextField(unique=True)
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
        return '%s%s' % ('x'*16,self.cardno[-4:])
    ccNumber = property(getCCNumber, setCCNumber)
    def __repr__(self):
        return u'%s' % self.cardno

    class Meta:
        db_table = 'apps_creditcard'
