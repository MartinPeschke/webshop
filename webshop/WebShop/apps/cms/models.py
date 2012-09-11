from django.db import models

__author__ = 'Martin'



class LinkGallery(models.Model):
    class Meta:
        db_table = 'apps_link_gallery'
    name = models.CharField(max_length=64, unique = True)

    def __unicode__(self):
        return self.name

class LinkGalleryItem(models.Model):
    class Meta:
        db_table = 'apps_link_gallery_item'
        ordering = ('sortOrder', )
    src = models.ImageField(upload_to= 'uploads')
    link = models.CharField(max_length=1024, blank=True, null=True)
    title = models.CharField(max_length=1024)
    description = models.TextField()
    sortOrder = models.IntegerField(default = 1)

    linkgallery = models.ForeignKey(LinkGallery)

