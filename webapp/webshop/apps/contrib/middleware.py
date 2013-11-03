import sys, traceback
from django.conf import settings
from django.template import Context
from django.core.cache import cache
from datetime import datetime

import webshop.utils.mail as mail
from webshop.apps.explore.models import Shop, Line, Promotion, ArticleOption
from webshop.apps.user.lib import get_role, is_in_signup
from webshop.apps.user.user_roles import simple_role, HAS_RIGHTS

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
            'USER_IS_IN_SIGNUP': is_in_signup(request.user),
            'host': request.get_host(),
            'shops': SHOPS,
            'default_lines': Line.objects.get_from_cache(settings.DEFAULT_SHOP),
            'default_shop': settings.DEFAULT_SHOP,
            'STATIC_TOKEN': settings.STATIC_VERSION_TOKEN,
            "FB_APP_ID":settings.FB_APP_ID,
            "FB_APP_SECRET":settings.FB_APP_SECRET
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
            mail.create_mail("webshop ERROR", settings.SERVER_EMAIL, settings.ERROR_MAIL, 'error_email', c)
        return None
