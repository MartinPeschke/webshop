from django.conf import settings
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response


from WebShop.apps.user.models import  Line, ArticleFamily, ArticleType
from WebShop.urls import SHOPS


LOCALES  = [l[0] for l in settings.LANGUAGES]
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