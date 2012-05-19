from django.contrib import admin
from WebShop.apps.slideshow.models import SlideShow, SlideShowItem

__author__ = 'Martin'


class SlideShowAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
admin.site.register(SlideShow, SlideShowAdmin)

class SlideShowItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'src', 'link', 'title', 'description')
admin.site.register(SlideShowItem, SlideShowItemAdmin)