from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _

from WebShop.apps.contrib.countries.models import Country

__author__ = 'Martin'

class Language(models.Model):
    class Meta:
        db_table = 'apps_language'
    code = models.CharField(max_length=2, primary_key = True)
    name = models.CharField(max_length=256)
    enabled = models.BooleanField(default = True)
    def __unicode__(self):
        return self.name

class AddressType(models.Model):
    class Meta:
        db_table = 'apps_address_type'
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        if self.name =='billing':
            return _('Rechnungsadresse')
        elif self.name =='shipping':
            return _('Lieferadresse')

class Address(models.Model):
    type = language = models.ForeignKey(AddressType)

    street = models.CharField(max_length=255)
    city = models.CharField(max_length=64)
    zip = models.CharField(max_length=16)
    country = models.ForeignKey(Country)
    language = models.ForeignKey(Language)
    tel = models.CharField(max_length=32)
    mobile = models.CharField(max_length=32, blank=True)
    fax = models.CharField(max_length=32, blank=True)

    # Relationship
    user = models.ForeignKey(User)
    def __str__(self):
        return "<Address %s for %s>" %(self.type, self.user_id)

    class Meta:
        db_table = 'apps_address'

    class Admin:
        list_display = ('user', 'type', 'country', 'city')