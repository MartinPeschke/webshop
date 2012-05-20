from django.contrib import admin
from WebShop.apps.cms.models import LinkGalleryItem, LinkGallery

__author__ = 'Martin'

class LinkGalleryItemInline(admin.TabularInline):
    model = LinkGalleryItem
    list_display = ('id', 'src', 'link', 'title', 'description')
    ordering = ['sortOrder']
    extra = 1

class LinkGalleryAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = [
        LinkGalleryItemInline,
    ]
admin.site.register(LinkGallery, LinkGalleryAdmin)
