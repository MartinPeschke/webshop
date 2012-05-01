from django.contrib.auth.models import User
from django.db import models

__author__ = 'Martin'

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