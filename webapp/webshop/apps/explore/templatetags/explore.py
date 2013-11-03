from operator import attrgetter
import os

from django import template
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template.loader import render_to_string

from webshop.apps.user.user_roles import simple_role, HAS_RIGHTS, NO_RIGHTS


register = template.Library()
FROM_PRICE_HTML_A = render_to_string('snippets/from_price_a.html',{})



# new filters, 2012

@register.filter
def get_option_img_tag(ao, shop_ref=None, classes = None):
    if ao.ref == '-':
        return '-'
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, shop_ref, 'options', ao.imgName)):
        return mark_safe('<img alt="{ao_ref}" class="small {classes}" src="/media/files/{shop_ref}/options/{img}"/>'.format(ao_ref = ao.ref, shop_ref = shop_ref, img = ao.imgName, classes = classes or ""))
    else:
        return mark_safe('%s' % ao.ref)



@register.filter
def get_single_option_list(article_options):
    aos = {}
    for l in article_options.values():
        aos.update({ao.ref:ao for ao in l})
    return sorted(aos.values(), key = attrgetter('ref'))



@register.simple_tag
def active(ref1, ref2):
    if ref1 == ref2: return 'active'
    return ''




# LEGACY

@register.filter
def simple_locale(locale_string):
    return 'de' in locale_string and 'de' or 'en'


@register.filter
def pathIsActive(uri, path):
    if(path[0] != '/' and path[-1] != '/'): path = "/%s/" % path
    if uri == path:
        return 'active'
    else: return ''

@register.filter
def selected(uri, path):
    if(path[0] != '/' and path[-1] != '/'): path = "/%s/" % path
    if uri == path:
        return 'selected'
    else: return ''

@register.filter
def selected_start(uri, path):
    uri = uri.split('/')
    if path in uri: #account for live per4.fcgi prefix
        return 'selected'
    else: 
        return ''

@register.filter
def pop(value):
    list = value.all()
    if list.count() > 0:
        return list[0].ref
    else:
        return ''

@register.filter
def get_cart_qty(cart, value):
    ao = None
    if cart:
        ao = cart._get_ItemDict().get(value,None)
        if ao: ao = ao.quantity
    return ao or 0

@register.filter
def price_by_role(pricing_set, role):
    # TODO: Update Database to use NULL instead of '' or 0 in DiscountPrices 
    prices = pricing_set.filter(forRole__in = (role in HAS_RIGHTS and HAS_RIGHTS or NO_RIGHTS)).filter(discountQty__isnull=True).order_by('forRole')
    if prices.count():
        return "%.2f" % prices[0].price
    else:
        return None

@register.filter
def discount_price_by_role(pricing_set, role):
    prices = pricing_set.filter(forRole__in = (role in HAS_RIGHTS and HAS_RIGHTS or NO_RIGHTS), discountQty__gt = 0).order_by('-forRole', 'discountQty')
    if prices.count():
        return mark_safe('<div class="discount_box rounded_elems"><span>%s</span>+</div> <span>%.2f</span>&euro;' % (prices[0].discountQty, prices[0].price))
    else:
        return mark_safe('<div style="display:none;">from <span>0</span> only <span>0</span></div>')

@register.filter
def has_ViewPrivilege(entity, role):
    return entity.has_privilege(role)

@register.filter
def has_PricePrivilege(user):
    if(user):
        return user.is_authenticated() and (user.get_profile().role in HAS_RIGHTS)
    else:
        return False

@register.filter
def getelem(dic, elem, default = []):
    return dic.get(elem, default)


@register.filter
def from_price(af, role):
    return getattr(af, 'price%s'%simple_role[role]) and render_to_string('snippets/from_price_b.html',\
                                                                         {'price':getattr(af, 'price%s'%role), 'has_more':getattr(af, 'has_more_%s'%simple_role[role])})\
                                                                         or FROM_PRICE_HTML_A



@register.simple_tag
def track_pagehits():
    if(not settings.DEBUG):
        return mark_safe(settings.GOOGLE_TRACKING)
    else:
        return ''


def check_image(af, subdir, shop_ref):
    return mark_safe('/'.join((settings.MEDIA_URL, 'files', shop_ref, subdir.replace('|', '/'), af.logopath + '.jpg')))


@register.filter
def type_logo(type_ref):
    return mark_safe('/'.join((settings.MEDIA_URL, 'files', 'types', '%s.jpg'%type_ref)))


@register.filter
def check_image_high(af, shop_ref):
    return check_image(af, 'families/high', shop_ref) 
@register.filter
def check_image_med(af, shop_ref):
    return check_image(af, 'families/medium', shop_ref) 
@register.filter
def check_image_low(af, shop_ref):
    return check_image(af, 'families/low', shop_ref) 
    

@register.filter
def path_exists(path):
    return os.path.exists(path)


@register.filter
def create_ao_imgtag(ao, shop_ref=None, classes = None):
    if ao.ref == '-':
    	return '-'
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, shop_ref, 'options', ao.imgName)):
        return mark_safe('<div title="{ao_ref}" class={classes}><img alt="{ao_ref}" class="small" src="/media/files/{shop_ref}/options/{img}"/></div>'.format(ao_ref = ao.ref, shop_ref = shop_ref, img = ao.imgName, classes = classes or ""))
    else:
        return mark_safe('<span name="%s" class="optionLink">%s</span>' % (ao.ref, ao.ref))

@register.filter
def truncate(stringthing, length=None):
    return stringthing[0:length] + (length<len(stringthing) and '...' or '')

@register.filter
def locale(lp, local):
    local = local[:2].lower()
    try:
        return (hasattr(lp, local) and getattr(lp, local)) or lp.en or _('Misc')
    except AttributeError:
        return ''

