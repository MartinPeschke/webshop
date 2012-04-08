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

def shop(request, shop_ref=settings.DEFAULT_SHOP):
    '''
    Shop Page, e.g http://www.per-4.com/piercing/
    '''
    return line(request, shop_ref, Line.objects.get_from_cache(shop_ref)[0][0].ref)

def _new_sale(request, shop, line, lang='en', role='E'):
    query = shop.promotion_set.filter(is_sale = ('sale' in line.ref)).filter(is_active=True).select_related('family').\
            extra(select={'is_null': "apps_articlefamily.min_price_%s is NULL" % role}).\
            order_by('is_null', '-create_time', 'apps_articlefamily.min_price_%s'%role)
    if(not query.count()):
        l = shop.line_set.order_by('sort')[1:2].get()
        return _line(request, shop, l, lang, role)

    query = map(lambda p: p.family, query.all()) # woulda loved to select the families directly, dont know how cept with pure sql or alchemy
    
    return query, {'show_header_img': True}, line

def _line(request, shop, line, lang='en', role='E'):
    '''
    Line page, e.g http://www.per-4.com/piercing/Titanium/
    '''
    query = ArticleFamily.objects.filter(line=line).\
        extra(select={'is_null': "min_price_%s is NULL" % role}).\
        order_by('is_null','min_price_%s'%role)
#===============================================================================
#    sort really like this???????
#===============================================================================
    art_type_id = request.GET.get('t', 0)
    art_type = None
    try:
        art_type = line.articletype_set.get(id=int(art_type_id))
    except:
        pass
    else:
        query = query.filter(art_type_id = art_type.id)
    return query, {'art_type':art_type,
                   'show_header_img':not bool(art_type)}, line

TEMPLATEHANDLER = {'line_new.html':_new_sale,'line_sale.html':_new_sale, 'line_html':_line}
def line(request, shop_ref, line_ref = None):
    try:
        shop = SHOPS[shop_ref]
    except:
        raise Http404
    lang = request.LANGUAGE_CODE[:2].lower()
    if lang not in LOCALES:
        lang = 'en'

    toplevel = Line.objects.get_from_cache(shop_ref)
    try:
        line = Line.objects.get(shop__ref=shop_ref, ref=line_ref)
    except Line.DoesNotExist:
        line = toplevel[0][0]
    
    art_type_id = request.GET.get('t', 0)
    try: 
        art_type_id = long(art_type_id)
    except:
        art_type_id = 0
    
    secondlevel = line.articletype_set.order_by(lang, 'en')
    
    role = simple_role[get_role(request.user)]

    line.logopath = (line.logopath or '').replace(u'{{LOCALE}}', lang)
    line_html = cache.get('line_page_%s_%s_%s_%s' % (line.id, request.GET.get('t', None), role, lang), False)
    context = {}
    if line_html == False:
        print 'cache update for ', 'explore/line_page_%s_%s_%s_%s' % (line.id, request.GET.get('t', None), role, lang)
        page, context, line = (TEMPLATEHANDLER.get(line.template_path, None) or _line)(request, shop, line, lang, role)
        for af in page:
            af.shop_ref = shop_ref
            af.url = urllib.quote("/%s/%s/%s/" % (shop_ref, af.line.ref, af.ref))
        query_count = len(page)
        secondlevel = line.articletype_set.order_by(lang, 'en')
        context.update(locals())
        line_html = mark_safe(render_to_string('explore/line_page.html', context,  context_instance=RequestContext(request)))
        cache.set('line_page_%s_%s_%s_%s' % (line.id, request.GET.get('t', None), role, lang), line_html, settings.CACHE_TIMEOUT)
    
    context.update(locals())
    return render_to_response('explore/line.html', context, context_instance=RequestContext(request))


def _get_articles(af, role):
	article_set = af.article_set.order_by('thickness', 'diameter_length', 'ref').all()

	pricing_set = Pricing.objects.filter(article__article_family = af).filter(forRole = role).order_by('discountQty').all()
	pricings = {}
	has_discount = False
	has_old_price = False
	for p in pricing_set:
		pricings[p.article_id] = pricings.get(p.article_id, []) + [p]
		has_discount = has_discount or len(pricings[p.article_id]) > 1
		has_old_price = has_old_price or bool(p.old_price)
	option_set = ArticleOption.objects.filter(article__article_family = af).all()
	options = {}
	for ao in option_set:
		 options[ao.article_id] = options.get(ao.article_id, []) + [ao]
	return article_set, options, pricings, has_old_price, has_discount

def article(request, shop_ref, line_ref, af_ref = None):
    if request.method == 'POST':
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/main/'))
    try:
        shop = SHOPS[shop_ref]
    except:
        raise Http404


    lang = request.LANGUAGE_CODE[:2].lower()
    if lang not in LOCALES:
        lang = 'en'
    toplevel = Line.objects.get_from_cache(shop_ref)
    
    af = None
    line = None
    try:
        af = ArticleFamily.objects.select_related('line').get(ref=af_ref)
    except ArticleFamily.DoesNotExist: 
        try:
            af = ArticleFamily.objects.select_related('line').get(pk=af_ref)
        except:
            raise Http404
            
    af.shop_ref = shop_ref
    line = af.line
    secondlevel = line.articletype_set.order_by(lang).all()

    query = ArticleFamily.objects.select_related().filter(line=line)
    art_type = None
    try:
        art_type = ArticleType.objects.get(id = af.art_type_id)
    except:
        pass
    else:
        query = query.filter(art_type_id = art_type.id)
    if art_type:
        art_type_id = art_type.id
    else:
        art_type_id = 0

    also_bought = ArticleFamily.objects.filter(pk__in=map(lambda x : x.also_bought_id, af.af1.order_by('-matches_count').all()[:24])).select_related('line__shop').all()
    
    role = simple_role[get_role(request.user)]
    article_set, options, pricings, has_old_price, has_discount_price = _get_articles(af, role)
    tablespan = 7 + has_old_price + has_discount_price
    show_state = 1

    a = render_to_response('explore/article.html', locals(), context_instance=RequestContext(request))

    return a

@json
def pane(request, type_id):
    lang = request.LANGUAGE_CODE[:2].lower()
    if lang not in LOCALES:
        lang = 'en'    
    show_state = 1

    try:
      art_type = ArticleType.objects.get(pk=type_id)
    except ArticleType.DoesNotExist:
      return {'body': ""}
    type_html = cache.get('type_page_%s_%s' % (art_type.en, show_state), False)
    if type_html == False:
        print 'cache miss for ', 'type_page_%s_%s' % (art_type.en, show_state)
        always_show_all = show_all = request.session.get('always_show_all', False)
        ats = ArticleType.objects.filter(en = art_type.en).filter(line__shop = art_type.line.shop).all()
        other_materials = ArticleFamily.objects.filter(art_type_id__in=map(lambda x : x.id, ats)).select_related('line__shop').order_by('line__ref', 'ref').all()
        type_html = mark_safe(render_to_string('explore/article_pane.html', locals(),  context_instance=RequestContext(request)))    
        cache.set('type_page_%s_%s' % (art_type.en, show_state), type_html, settings.CACHE_TIMEOUT)
    else:
        print 'cache hit for ', 'type_page_%s_%s' % (art_type.en, show_state)
    type_html = cache.get('type_page_%s_%s' % (art_type.en, show_state))
    
    return {'body': type_html}
