from django.contrib import admin

from WebShop.apps.user.models import Profile
from WebShop.apps.user.models.password_token import PasswordToken

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company_name', 'first_name', 'last_name', 'create_time')
    search_fields = ( 'company_name' , 'first_name', 'last_name', )
admin.site.register(Profile, ProfileAdmin)

class PasswordTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'value', 'create_time')
    search_fields = ( 'user__email', )
admin.site.register(PasswordToken, PasswordTokenAdmin)

