from django.contrib import admin
from WebShop.apps.slideshow.models import SlideShow, SlideShowItem

__author__ = 'Martin'

class SlideShowItemInline(admin.TabularInline):
    model = SlideShowItem
    list_display = ('id', 'src', 'link', 'title', 'description')
    ordering = ['sortOrder']
    extra = 1

class SlideShowAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = [
        SlideShowItemInline,
    ]
admin.site.register(SlideShow, SlideShowAdmin)
