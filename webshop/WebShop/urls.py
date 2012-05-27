from django.http import HttpResponseRedirect
from WebShop.apps.explore.models import Shop, Line, ArticleFamily
from django.conf import settings

from django.conf.urls import *
from django.contrib.sitemaps import GenericSitemap
from WebShop.apps.contrib.static_sitemap import StaticSitemap  

# The next two lines enable the admin and load each admin.py file:
from django.contrib import admin
admin.autodiscover()

shops_dict = {
    'queryset': Shop.objects.all(),
    # 'date_field': 'pub_date',
}

SHOPS = dict([(shop.ref, shop) for shop in shops_dict['queryset']])
SHOPS_URLS = '|'.join(SHOPS.iterkeys())

lines_dict = {
    'queryset': Line.objects.all(),
    # 'date_field': 'pub_date',
}

afs_dict = {
    'queryset': ArticleFamily.objects.all(),
    # 'date_field': 'pub_date',
}


sitemaps = {
    'pages': StaticSitemap(),
    'shops': GenericSitemap(shops_dict, priority=0.5),
    'lines': GenericSitemap(lines_dict, priority=0.6),
    'afs': GenericSitemap(afs_dict, priority=1.0),
}

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),

    # Real Index Page
    url(r'^$', 'WebShop.apps.cms.pages.main', name='home-route'),
    url(r'^main/?$',  lambda x: HttpResponseRedirect('/')),

    # Browsing
    (r'^(?P<shop_ref>%s)/$' % SHOPS_URLS, 'WebShop.apps.explore.views.handler.shop'),
    (r'^pane/(?P<type_id>\d+)/$' , 'WebShop.apps.explore.views.handler.pane'),

    (r'^(?P<shop_ref>%s)/(?P<line_ref>[\w\d\-_]+)/$' % SHOPS_URLS, 'WebShop.apps.explore.views.handler.line'),
    (r'^(?P<shop_ref>%s)/(?P<line_ref>[\w\d\-_]+)/(?P<af_ref>[\w\d\-_. ]+)/$' % SHOPS_URLS, 'WebShop.apps.explore.views.handler.article'),

    # Static
    (r'^news/$', 'WebShop.apps.cms.pages.news'),
    (r'^downloads/$', 'WebShop.apps.cms.pages.downloads'),
    (r'^contact/$', 'WebShop.apps.cms.pages.contact'),
    (r'^aboutus/$', 'WebShop.apps.cms.pages.aboutus'),
    (r'^agb/$', 'WebShop.apps.cms.pages.agb'),
    (r'^faq/$', 'WebShop.apps.cms.pages.faq'),
    (r'^jobs/$', 'WebShop.apps.cms.pages.jobs'),
    (r'^materials/$', 'WebShop.apps.cms.pages.materials'),
    (r'^impressum/$', 'WebShop.apps.cms.pages.impressum'),
    (r'^gallery/(?P<page>\d*)$', 'WebShop.apps.cms.pages.gallery'),
    (r'^ourads/$', 'WebShop.apps.cms.pages.ourads'),
    (r'^coupons/$', 'WebShop.apps.cms.pages.coupons'),
    (r'^shipping/$', 'WebShop.apps.cms.pages.shipping'),
    (r'^studios/$', 'WebShop.apps.cms.pages.studios'),
    (r'^seminar/$', 'WebShop.apps.cms.pages.seminar'),
    (r'^convention/$', 'WebShop.apps.cms.pages.convention'),
    (r'^content/(?P<page>[a-zA-Z0-9_-]*)$', 'WebShop.apps.cms.pages.generic'),

    # Search
    (r'^search/', 'WebShop.apps.search.views.index'),

    # User
    (r'^user/', include('WebShop.apps.user.urls')),
    # Order
    (r'^order/', include('WebShop.apps.order.urls')),
    (r'^cms/', include('WebShop.apps.cms.urls')),

    # Web Service
    (r'^services/', include('WebShop.apps.service.urls')),

    # media
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

    # i18n
    (r'^i18n/', include('django.conf.urls.i18n')),

    # Sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})
)
