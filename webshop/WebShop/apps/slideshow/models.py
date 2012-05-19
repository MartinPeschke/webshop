from django.db import models

__author__ = 'Martin'



class SlideShow(models.Model):
    class Meta:
        db_table = 'apps_slideshow'
    name = models.CharField(max_length=64, unique = True)

    def __unicode__(self):
        return self.name

class SlideShowItem(models.Model):
    class Meta:
        db_table = 'apps_slideshow_item'
    src = models.ImageField(upload_to= 'uploads')
    link = models.CharField(max_length=1024)
    title = models.CharField(max_length=1024)
    description = models.TextField()
    slideshow = models.ForeignKey(SlideShow)

