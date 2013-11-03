from django.http import HttpResponseRedirect
from webshop.apps.explore.models import Shop, Line, ArticleFamily
from django.conf import settings

from django.conf.urls import *
from django.contrib.sitemaps import GenericSitemap
from webshop.apps.contrib.static_sitemap import StaticSitemap

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
    (r'^/?$', 'webshop.apps.cms.pages.welcome'),
    url(r'^main/$', 'webshop.apps.cms.pages.main', name='home-route'),
    # Browsing
    (r'^(?P<shop_ref>%s)/$' % SHOPS_URLS, 'webshop.apps.explore.views.handler.shop'),
    (r'^pane/(?P<type_id>\d+)/$' , 'webshop.apps.explore.views.handler.pane'),

    (r'^(?P<shop_ref>%s)/(?P<line_ref>[\w\d\-_]+)/$' % SHOPS_URLS, 'webshop.apps.explore.views.handler.line'),
    (r'^(?P<shop_ref>%s)/(?P<line_ref>[\w\d\-_]+)/(?P<af_ref>[\w\d\-_. ]+)/$' % SHOPS_URLS, 'webshop.apps.explore.views.handler.article'),

    # Static
    (r'^news/$', 'webshop.apps.cms.pages.news'),
    (r'^downloads/$', 'webshop.apps.cms.pages.downloads'),
    url(r'^contact/$', 'webshop.apps.cms.pages.contact', name="contact-route"),
    url(r'^aboutus/$', 'webshop.apps.cms.pages.aboutus', name="aboutus-route"),
    (r'^agb/$', 'webshop.apps.cms.pages.agb'),
    (r'^faq/$', 'webshop.apps.cms.pages.faq'),
    (r'^jobs/$', 'webshop.apps.cms.pages.jobs'),
    (r'^materials/$', 'webshop.apps.cms.pages.materials'),
    url(r'^impressum/$', 'webshop.apps.cms.pages.impressum', name="imprint-route"),
    (r'^gallery/(?P<page>\d*)$', 'webshop.apps.cms.pages.gallery'),
    (r'^coupons/$', 'webshop.apps.cms.pages.coupons'),
    (r'^shipping/$', 'webshop.apps.cms.pages.shipping'),
    (r'^studios/$', 'webshop.apps.cms.pages.studios'),
    (r'^seminar/$', 'webshop.apps.cms.pages.seminar'),
    (r'^convention/$', 'webshop.apps.cms.pages.convention'),
    (r'^content/(?P<page>[a-zA-Z0-9_-]*)$', 'webshop.apps.cms.pages.generic'),

    # Search
    (r'^search/', 'webshop.apps.search.views.index'),

    # User
    (r'^user/', include('webshop.apps.user.urls')),
    # Order
    (r'^order/', include('webshop.apps.order.urls')),
    (r'^cms/', include('webshop.apps.cms.urls')),

    # Web Service
    (r'^services/', include('webshop.apps.service.urls')),

    # media
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

    # i18n
    (r'^i18n/', include('django.conf.urls.i18n')),

    # Sitemaps
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps})
)
