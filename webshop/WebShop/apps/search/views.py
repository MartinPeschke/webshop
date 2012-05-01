from WebShop.apps.explore.models import ArticleFamily
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
import urllib

def index(request):
    searchstring = request.GET.get('s', False)
    if searchstring:       
        page = ArticleFamily.objects.extra(where=['match(`search_index`) against("*%s*" in boolean mode)' % searchstring])\
               .filter(line__shop__allowed_shops__icontains = settings.SHOP_NAME).select_related('line__shop').all()
        for af in page:
            af.shop_ref = af.line.shop.ref
            af.url = urllib.quote("/%s/%s/%s/" % (af.shop_ref, af.line.ref, af.ref))            
            
    return render_to_response('search/search_result.html', locals(), context_instance=RequestContext(request))

def shopsearch(request, shop_ref = settings.DEFAULT_SHOP):
    searchstring = request.GET.get('s', False)
    if searchstring:       
        page = ArticleFamily.objects.extra(where=['match(`search_index`) against("*%s*" in boolean mode)' % searchstring])\
                .filter(line__shop__ref = shop_ref).select_related('line__shop').all()
        for af in page:
            af.shop_ref = af.line.shop.ref
            af.url = urllib.quote("/%s/%s/%s/" % (af.shop_ref, af.line.ref, af.ref))            
            
    return render_to_response('search/search_result.html', locals(), context_instance=RequestContext(request))