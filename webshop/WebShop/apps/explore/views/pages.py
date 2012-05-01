import os
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext, TemplateDoesNotExist

def render_with_locale(request, template, context):
    rctxt = RequestContext(request)
    context.update({'short_locale':rctxt['LANGUAGE_CODE'][:2].lower()})
    short_locale = rctxt['LANGUAGE_CODE'][:2].lower()
    try:
        return render_to_response('pages/%s_%s.html' % (template, short_locale), context, context_instance=rctxt)
    except TemplateDoesNotExist:
        return render_to_response('pages/%s_en.html' % template, context, context_instance=rctxt)

def main(request):
    return render_with_locale(request, 'main', locals())

def news(request):
    return render_to_response('pages/news.html', locals(), context_instance=RequestContext(request))

def materials(request):
    return render_with_locale(request, 'material', locals())

def downloads(request):
    return render_with_locale(request, 'downloads', locals())

def contact(request):
	return render_to_response('pages/contact.html', locals(), context_instance=RequestContext(request))

def studios(request):
    return render_with_locale(request, 'studios', locals())

def aboutus(request):
    return render_with_locale(request, 'aboutus', locals())
def faq(request):
    return render_with_locale(request, 'faq', locals())

def agb(request):
    return render_with_locale(request, 'agb', locals())

def jobs(request):
    return render_with_locale(request, 'jobs', locals())

def impressum(request):
    return render_with_locale(request, 'impressum', locals())
def seminar(request):
    return render_with_locale(request, 'seminar', locals())
def convention(request):
    return render_with_locale(request, 'convention_einladung', locals())

def gallery(request, page = 1):
    fields = {1: 'Lukas Zpira Seminar 4. - 5. Oktober 2008',
              2: 'Lukas Zpira Seminar 4. - 5. Oktober 2008'}
    if not page: 
        page = 1
    i = int(page)        
    next = fields.get(i+1, False) and i+1
    prev = fields.get(i-1, False) and i-1
    title = fields.get(i, None)
    
    
    return render_with_locale(request, 'gallery', locals())

def coupons(request):
    return render_with_locale(request, 'coupons', locals())

def shipping(request):
    return render_with_locale(request, 'shipping', locals())

def generic(request, page):
    return render_with_locale(request, page, locals())

def ourads(request):
    ad_path = os.path.join(settings.MEDIA_ROOT, 'ads')
    files = [(fname[3:], fname[3:].split('.')[0]) \
                for fname in os.listdir(ad_path) \
                if fname[0:3] == 'TN_' and \
                    os.path.exists(os.path.join(ad_path, fname[3:])) and \
                    os.path.exists(os.path.join(ad_path,"M_%s"%fname[3:]))]
    files.reverse()
    print files
    
    return render_with_locale(request, 'ourads', locals())