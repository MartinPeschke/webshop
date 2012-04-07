from WebShop.apps.contrib.decorator import json
from WebShop.apps.explore.models import Shop, Line, ArticleFamily, ArticleOption, ArticleType, Promotion, Pricing
from WebShop.apps.explore.templatetags.explore import check_image
from WebShop.apps.explore.views import *
from WebShop.apps.user import get_role, simple_role
from WebShop.utils.etl import NO_RIGHTS, HAS_RIGHTS
from WebShop.urls import SHOPS

from django.conf import settings 

from django.core.cache import cache
from django.core.paginator import Paginator
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe 
from django.template import RequestContext, Context, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.shortcuts import render_to_response, get_object_or_404


LOCALES  = [l[0] for l in settings.LANGUAGES]
from datetime import datetime, date
from decimal import *
from time import time
import urllib


def home(request):
	context = {"home_article_types":ArticleType.objects.get_types(settings.SHOP_NAME)}
	return render_to_response('pages/main_en.html', context, context_instance=RequestContext(request))

def types(request, shop_ref, type_ref):
	shop = SHOPS[shop_ref]
	toplevel = Line.objects.get_from_cache(shop_ref)
	role = 'E'
	type = ArticleType.objects.get_from_cache(settings.SHOP_NAME, type_ref)
	context = {
			'art_type':type,
			'show_header_img':False,
			'page': ArticleFamily.objects.filter(art_type_id__in=type.id.split(',')).\
					extra(select={'is_null': "min_price_%s is NULL" % role}).\
					order_by('is_null','min_price_%s'%role).all()
			}
	for af in context['page']:
		af.shop_ref = shop.ref
		af.url = urllib.quote("/%s/%s/%s/" % (shop_ref, af.line.ref, af.ref))
	context['line_html'] = mark_safe(render_to_string('explore/line_page.html', context,  context_instance=RequestContext(request)))
	return render_to_response('explore/line.html', context, context_instance=RequestContext(request))