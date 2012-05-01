from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

__author__ = 'Martin'

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