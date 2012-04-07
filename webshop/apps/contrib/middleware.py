import WebShop.utils.mail as mail
from WebShop.utils.etl import ANONYMOUS_ROLE, HAS_RIGHTS
from WebShop.apps.explore.models import Promotion, ArticleOption
from django.conf import settings
from django.contrib.auth.models import *
from django.http import HttpResponse
from django.template import Context
from django.core.cache import cache
from datetime import datetime

from email.Iterators import body_line_iterator
import sys, traceback

from WebShop.apps.explore.models import Shop, Line
from WebShop.apps.user import get_role, simple_role
from django.conf import settings

SHOPS = Shop.objects.filter(allowed_shops__icontains = settings.SHOP_NAME).order_by('sort').all()

class CampaignTracker(object):
    def process_request(self, request):
        if request.GET.get('cid'):
            cidlist = request.session.get('cid_list', [])
            cidlist.append({'cid':request.GET.get('cid'), 'timestamp':datetime.now(), 'referer':request.META.get('HTTP_REFERER')})
            request.session['cid_list'] = cidlist
        return None


def cart_shops_processor(request):
    role = get_role(request)
    return {'request' : request,
            'cart': request.session.get('cart',[]),
            'role': role,
            'simple_role': simple_role[role],
            'has_rights' : (role in HAS_RIGHTS) and True or False,
            'host': request.META['HTTP_HOST'],
            'shops': SHOPS,
            'default_lines': Line.objects.get_from_cache(settings.DEFAULT_SHOP),
            'default_shop': settings.DEFAULT_SHOP
            }

def random_promo_processor(request):
	total_article_count = cache.get('total_article_count')
	if not total_article_count:
		count = ArticleOption.objects.filter(article__article_family__line__shop__allowed_shops__icontains = settings.SHOP_NAME).count()
		count -= count%10
		cache.set('total_article_count', count)
		total_article_count = cache.get('total_article_count')
	return {'random_new': Promotion.objects.get_random_new(), 'total_article_count':total_article_count}

class ErrorEmailingMiddleware:

    def process_exception(self, request, exception):
        if request.user.is_authenticated():
            user = (request.user.id, request.user.username, ['%s' % g for g in request.user.groups.all()], request.user.email)
        else:
            user = 'anonymous'
        print 'Encounting error, sending error mail to %s' % settings.ERROR_MAIL
        c = Context({'user': user,
            'stacktrace': ''.join(traceback.format_tb(sys.exc_info()[2])),
            'error': exception,
            'request': request})
        if not settings.DEBUG:
            mail.create_mail("WebShop ERROR", settings.SERVER_EMAIL, settings.ERROR_MAIL, 'error_email', c)
        return None
