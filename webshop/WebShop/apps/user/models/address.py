from django.contrib.auth.models import User
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
__author__ = 'Martin'


ADDRESS_TYPES = (
    ('billing', mark_safe(_('Billing Address'))),
    ('shipping', mark_safe(_('Shipping Address'))),
    )

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