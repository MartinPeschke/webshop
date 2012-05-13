from django.contrib import admin
from .models import Order

__author__ = 'Martin'


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)
admin.site.register(Order, OrderAdmin)
