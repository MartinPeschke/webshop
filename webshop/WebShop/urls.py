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
    url(r'^$', 'WebShop.apps.explore.views.pages.main', name='home-route'),

    # Browsing
    (r'^(?P<shop_ref>%s)/$' % SHOPS_URLS, 'WebShop.apps.explore.views.handler.shop'),
    (r'^pane/(?P<type_id>\d+)/$' , 'WebShop.apps.explore.views.handler.pane'),

    (r'^(?P<shop_ref>%s)/(?P<line_ref>[\w\d\-_]+)/$' % SHOPS_URLS, 'WebShop.apps.explore.views.handler.line'),
    (r'^(?P<shop_ref>%s)/(?P<line_ref>[\w\d\-_]+)/(?P<af_ref>[\w\d\-_. ]+)/$' % SHOPS_URLS, 'WebShop.apps.explore.views.handler.article'),

    # Static
    (r'^news/$', 'WebShop.apps.explore.views.pages.news'),
    (r'^downloads/$', 'WebShop.apps.explore.views.pages.downloads'),
    (r'^contact/$', 'WebShop.apps.explore.views.pages.contact'),
    (r'^aboutus/$', 'WebShop.apps.explore.views.pages.aboutus'),
    (r'^agb/$', 'WebShop.apps.explore.views.pages.agb'),
    (r'^faq/$', 'WebShop.apps.explore.views.pages.faq'),
    (r'^jobs/$', 'WebShop.apps.explore.views.pages.jobs'),
    (r'^materials/$', 'WebShop.apps.explore.views.pages.materials'),
    (r'^impressum/$', 'WebShop.apps.explore.views.pages.impressum'),
    (r'^gallery/(?P<page>\d*)$', 'WebShop.apps.explore.views.pages.gallery'),
    (r'^ourads/$', 'WebShop.apps.explore.views.pages.ourads'),
    (r'^coupons/$', 'WebShop.apps.explore.views.pages.coupons'),
    (r'^shipping/$', 'WebShop.apps.explore.views.pages.shipping'),
    (r'^studios/$', 'WebShop.apps.explore.views.pages.studios'),
    (r'^seminar/$', 'WebShop.apps.explore.views.pages.seminar'),
    (r'^convention/$', 'WebShop.apps.explore.views.pages.convention'),
    (r'^content/(?P<page>[a-zA-Z0-9_-]*)$', 'WebShop.apps.explore.views.pages.generic'),

    # Search
    (r'^search/', 'WebShop.apps.search.views.index'),

    # User
    (r'^user/', include('WebShop.apps.user.urls')),
    # Order
    (r'^order/', include('WebShop.apps.order.urls')),

    # Web Service
    (r'^services/', include('WebShop.apps.service.urls')),

    # media
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    # i18n
    (r'^i18n/', include('django.conf.urls.i18n')),

    # Sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})
)
