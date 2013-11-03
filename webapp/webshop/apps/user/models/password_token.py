from django.contrib.auth.models import User
from django.db import models

__author__ = 'Martin'


RESETPASSWORDTOKEN = 1
REGISTERNEWTOKEN = 2
APPROVALWHOLESALETOKEN = 3

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