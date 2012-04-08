from django.db import models, connection

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes import generic

from django.core.cache import cache
from django.utils.safestring import mark_safe

from WebShop.utils.etl import USER_ROLES, USER_GROUPS, HAS_RIGHTS, NO_RIGHTS
from WebShop.utils.jsonfield import JSONField
from django.conf import settings

from django.utils.translation import ugettext as _

import os, random

import logging
log = logging.getLogger(__name__)



def has_privilege(self, role):
    return self.viewableByRole <= role

def _get_I18N_default(idFieldName):
    def newfunc(self):
        if(getattr(self, idFieldName)):
            try:
                # lp = LanguagePack.objects.get(id = getattr(self, idFieldName))
                lp = LanguagePack.objects.get_from_cache(id = getattr(self, idFieldName))
            except Exception:
                lp = None
                print 'lp does not yet exist'
            return lp
        else:
            return None
    return newfunc

def _set_I18N_default(idFieldName):
    def newfunc(self, messages = {}):
        if(type(messages) in [str, unicode]):
            messages = {'en':messages}

        if(type(messages) == dict):
            if(getattr(self, idFieldName)):
                lp = LanguagePack.objects.get(id = getattr(self, idFieldName))
                for k, v in messages.iteritems():
                    if(k!='id'):
                        setattr(lp, k, v)
            else:
                lp = LanguagePack()
                for k, v in messages.iteritems():
                    if(k!='id'):
                        setattr(lp, k, v)
            try:
                lp.save()
            except Exception:
                print 'insertion error for LanguagePack, maybe encode', self.__class__.__name__, messages.get('en', '')
            setattr(self, idFieldName, lp.id)
        else:
            raise ValueError, 'The Messages provided are not of expected format ClassDict, but %s with %s' % (type(messages), messages)
        return None
    return newfunc

class Shop(models.Model):
    is_articleDB = True

    ref = models.CharField(max_length=48, unique=True)
    logopath = models.CharField(max_length=128, null=True, blank=True) # ImageField
    viewableByRole = models.CharField(max_length=2, null=True, blank=True)
    sort = models.IntegerField(null=True, default=0)
    allowed_shops = models.TextField(null=True)
    name_I18N_id = models.IntegerField()
    name = property(_get_I18N_default('name_I18N_id'), _set_I18N_default('name_I18N_id'))
    def __str__(self):
        return self.ref

    def get_absolute_url(self):
        return '/%s/' % self.ref

    has_privilege = has_privilege
    class Meta:
        db_table = 'apps_shop'

class LineManager(models.Manager):
    def get_from_cache(self, shop_ref):
        lines = cache.get('%s_lines' % shop_ref, False)
        if lines:
            return lines
        else:
            lines = [(l, 1) for l in Line.objects.filter(shop__ref=shop_ref).order_by('sort', 'ref')]
            shop = Shop.objects.get(ref = shop_ref)
            if(not shop.promotion_set.filter(is_active = True).filter(is_sale = True).count()):
                try:
                    Line.objects.get(ref = ('%s_sale'%shop_ref).lower())
                except Line.DoesNotExist:
                    pass
                else:
                    lines[-1] = (lines[-1][0], 0)
            if(not shop.promotion_set.filter(is_active = True).filter(is_new = True).count()):
                try:
                    Line.objects.get(ref = ('%s_new'%shop_ref).lower())
                except Line.DoesNotExist:
                    pass
                else:
                    lines[0] = (lines[0][0], 0)
            cache.set('%s_lines' % shop_ref, lines, settings.CACHE_TIMEOUT)
            return cache.get('%s_lines' % shop_ref)

class Line(models.Model):
    is_articleDB = True

    ref = models.CharField(max_length=48)
    logopath = models.CharField(max_length=128, null=True, blank=True)
    sort = models.IntegerField(null=True, default=0)
    viewableByRole = models.CharField(max_length=2, null=True, blank=True)
    
##TODO: check templates for different news and sales    
    template_path = models.CharField(max_length = 64, null=True, blank=True, default = 'line.html')
    
    shop = models.ForeignKey(Shop)

    name_I18N_id = models.IntegerField(null=True)
    name = property(_get_I18N_default('name_I18N_id'), _set_I18N_default('name_I18N_id'))

    objects = LineManager()
   
    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.ref)

    def get_absolute_url(self):
        return '/%s/%s/' % (self.shop.ref, self.ref)

    has_privilege = has_privilege
  
  
    def has_specialoffer(self):
        cursor = connection.cursor()
        cursor.execute(
            """select shop.ref, p.is_sale, count(p.id) 
                from apps_shop shop 
                left outer join apps_line line on line.shop_id = shop.id 
                left outer join apps_articlefamily af on line.id = af.line_id 
                left outer join apps_promotion p on p.family_id = af.id
                where (p.is_sale = 1 or p.is_new = 1)
                group by shop.id, p.is_sale 
                having count(p.id) > 0;""")
        row = cursor.fetchone()
        return row
        
    
    class Meta:
        db_table = 'apps_line'
        ordering = ['sort']

class ArticletypeManager(models.Manager):
	def get_types(self, allowed_shop):
		cache_key = 'shops_articletypes_%s'%allowed_shop
		p = ArticleType.objects.raw("""select apps_shop.ref as shop_ref, at_ref, 
									GROUP_CONCAT(apps_articletype.id SEPARATOR ',') as id, max(en) as en,max(de) as de,max(fr) as fr,max(es) as es,max(it) as it,max(pl) as pl,max(ch) as ch
									from apps_articletype
									join apps_line on apps_line.id = line_id
									join apps_shop on apps_shop.id = apps_line.shop_id
									where allowed_shops LIKE %s
									group by apps_shop.ref, at_ref
									order by apps_shop.ref, at_ref;""", ['%%%s%%'%allowed_shop])
		return p
	def get_from_cache(self, allowed_shop, type_ref):
		cache_key = 'types_%s' % type_ref
		type = cache.get(cache_key, None)
		if type:
			return type
		else:
			type = ArticleType.objects.raw("""select apps_shop.ref as shop_ref, at_ref, 
									GROUP_CONCAT(apps_articletype.id SEPARATOR ',') as id, max(en) as en,max(de) as de,max(fr) as fr,max(es) as es,max(it) as it,max(pl) as pl,max(ch) as ch
									from apps_articletype
									join apps_line on apps_line.id = line_id
									join apps_shop on apps_shop.id = apps_line.shop_id
									where allowed_shops LIKE %s and at_ref = %s
									group by apps_shop.ref, at_ref
									order by apps_shop.ref, at_ref;""", ['%%%s%%'%allowed_shop, type_ref])[0:1]
			if type:
				cache.set(cache_key, type[0], settings.CACHE_TIMEOUT)
				return type[0]
			else:
				return None

class ArticleType(models.Model):
	'''
	ArticleType is near identical to LP, might change in future
	'''
	is_articleDB = True

	line = models.ForeignKey(Line)
	at_ref = models.CharField(max_length=255)
	shop_ref = models.CharField(max_length=255)
	en = models.CharField(max_length=255)
	de = models.CharField(null=True, blank = True, max_length=255)
	fr = models.CharField(null=True, blank = True, max_length=255)
	it = models.CharField(null=True, blank = True, max_length=255)
	pl = models.CharField(null=True, blank = True, max_length=255)
	es = models.CharField(null=True, blank = True, max_length=255)
	ch = models.CharField(null=True, blank = True, max_length=255)

	create_time = models.DateTimeField(auto_now_add=True)
	update_time = models.DateTimeField(auto_now=True)
	objects = ArticletypeManager()
	def __str__(self):
		return '<ArticleType %s for Line %s>' % (self.en, self.line.ref)

	class Meta:
		db_table = 'apps_articletype'



class ArticleFamily(models.Model):
    is_articleDB = True

    also_bought = models.ManyToManyField("self", through='AlsoBought', symmetrical = False)
    min_price_E = models.FloatField()
    min_price_K = models.FloatField()
    has_more_E = models.NullBooleanField(null=True, blank=True)
    has_more_K = models.NullBooleanField(null=True, blank=True)
    search_index = models.TextField(null=True, blank = True)
    
    def setPriceE(self, value):
        self.min_price_E = round(value * 1000) / 1000
    def getPriceE(self):
        if(self.min_price_E):
            return round(self.min_price_E * 100) / 100
        else:
            return self.min_price_E
    priceE = property(getPriceE, setPriceE)
    def setPriceK(self, value):
        self.min_price_K = round(value * 1000) / 1000
    def getPriceK(self):
        if(self.min_price_K):
            return round(self.min_price_K * 100) / 100
        else:
            return self.min_price_K
    priceK = property(getPriceK, setPriceK)



    ref = models.CharField(max_length=64, unique=True)
    logopath = models.CharField(max_length=128, null=True, blank=True) # ImageField
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    desc_I18N_id = models.IntegerField(null=True)
    desc = property(_get_I18N_default('desc_I18N_id'), _set_I18N_default('desc_I18N_id'))
    
    body_part = models.CharField(null=True, blank=True, max_length=255)
    
    line = models.ForeignKey(Line)
    art_type_id = models.IntegerField()


    def _get_promotion(self):
        return Promotion.objects.get_from_cache(self)
    promotion = property(_get_promotion)
    

    def get_line_ref(self):
        key = 'line_ref_%s' % self.line_id
        value = cache.get(key, False)
        if value:
            return value
        else:
            cache.set(key, self.line.ref, 600)
            return cache.get(key)
        
    def has_privilege(self, role):
        return self.line.has_privilege(role)

    def get_shop_ref(self):
        key = 'shop_ref_%s' % self.line_id
        value = cache.get(key, False)
        if value:
            return value
        else:
            cache.set(key, self.line.shop.ref, 600)
        return cache.get(key)

    def getArtType(self):
        return ArticleType.objects.get(id=self.art_type_id)

    def __str__(self):
        return "<%s %s>" % (self.__class__.__name__, self.ref)

    def get_absolute_url(self):
        return '/%s/%s/%s/' % (self.line.shop.ref, self.line.ref, self.ref)

    class Meta:
        ordering = ['-update_time', 'ref']
        db_table = 'apps_articlefamily'

class AlsoBought(models.Model):
    is_articleDB = True

    bought_this = models.ForeignKey(ArticleFamily, related_name="af1")
    also_bought = models.ForeignKey(ArticleFamily, related_name="af2")
    matches_count = models.IntegerField(null=True)
    class Meta:
        db_table = 'apps_alsobought'

class PromotionManager(models.Manager):
    def get_random_new(self, count = 3):
        p = cache.get('new_promotions', False)
        if p == False:
            try:
                p = Promotion.objects.filter(is_new = True).filter(family__line__shop__allowed_shops__icontains = settings.SHOP_NAME).filter(is_active=True).select_related('family__line__shop').all()
                cache.set('new_promotions', p, settings.CACHE_TIMEOUT)
            except Promotion.DoesNotExist:
                cache.set('new_promotions', None, settings.CACHE_TIMEOUT)
            p = cache.get('new_promotions')
        result = []
        if(p):
            for i in range(count):
                result.append(p[random.randint(0, len(p)-1)])
        return result

    def get_from_cache(self, af, type = None):
        p = cache.get('promotion_%s' % af.id, False)
        if p == False:
            try:
                p = Promotion.objects.filter(family = af).filter(is_active = True).order_by('-create_time')
                if(type):
                    p = p.filter(type = type)
                p = p[0:1].get()
                cache.set('promotion_%s' % af.id, p, settings.CACHE_TIMEOUT)
            except Promotion.DoesNotExist:
                cache.set('promotion_%s' % af.id, None, settings.CACHE_TIMEOUT)
        return cache.get('promotion_%s' % af.id)


class Promotion(models.Model):
    '''
    Promotion to attach to ArticleFamilies can be New or Sale
    '''
    is_articleDB = True

    family = models.ForeignKey(ArticleFamily)
    shop = models.ForeignKey(Shop)
    desc_I18N_id = models.IntegerField(null=True, blank = True)
    desc = property(_get_I18N_default('desc_I18N_id'), _set_I18N_default('desc_I18N_id'))
    logopath = models.CharField(max_length=128, null=True, blank=True) # ImageField
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.NullBooleanField(null=True, blank=True, default = True)

    objects = PromotionManager()

    def get_shop_ref(self):
        key = 'shop_ref_%s' % self.family.line_id
        value = cache.get(key, False)
        if value:
            return value
        else:
            cache.set(key, self.shop.ref, 600)
            return cache.get(key)

    def _getRef(self):
        return self.family.ref
    ref = property(_getRef)

    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    is_sale = models.BooleanField(default = True)
    is_new = models.BooleanField(default = False)
    is_newprice = models.BooleanField(default = False)
    is_newsize = models.BooleanField(default = False)

    def _get_type(self):
        return self.is_newsize * 8 | self.is_newprice * 4 | self.is_new * 2 | self.is_sale
    def _get_type_ref(self): # needed for Templates to easily find their icon
        return  self.is_sale and 'sale' or \
                self.is_new and 'new' or \
                self.is_newprice and 'price' or \
                self.is_newsize and 'size'
    type_ref = property(_get_type_ref)
    
    def save(self):
        if self.family_id and not self.shop_id:
            self.shop = self.family.line.shop
        super(Promotion, self).save()

    class Meta:
        db_table = 'apps_promotion'
        ordering = ['family']

    def __repr__(self):
        return "<%s for %s>" % (self.__class__.__name__, self.family.ref)




class Article(models.Model):
    is_articleDB = True

    ref = models.CharField(max_length=255, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    # for trunk version
    diameter_length = models.FloatField(null=True, blank=True)
    ball_size1 = models.FloatField(null=True, blank=True)
    ball_size2 = models.FloatField(null=True, blank=True)
    thickness = models.FloatField(null=True, blank=True)
    measure = models.CharField(max_length=4, null=True, blank=True)
    packaging_unit = models.IntegerField(null=True)

    def getCompiledSize(self):
#===============================================================================
#            balls = '/'.join(filter(lambda x: x, [self.ball_size1, self.ball_size2]))
#            return mark_safe('&nbsp;x&nbsp;'.join(filter(lambda x: x, ['%.1f' % self.thickness, self.diameter_length, balls])))
#===============================================================================
        result = []
        if(self.thickness):
            result = self.thickness and "&nbsp;%s%s%s%s" % \
                             (self.thickness and round(self.thickness, 3) or '', 
                              (self.diameter_length and " x %s" % round(self.diameter_length, 3) or ''),
                              (self.ball_size1 and ' x %s' % self.ball_size1) or '', 
                              (self.ball_size2 and '/%s ' % self.ball_size2) or '')
            if(self.measure):
                result = result.rstrip() + '%s' % self.measure
            result=[result]
        if(self.packaging_unit):
            result[0:0] = ['%s %s' % (self.packaging_unit,_('pcs'))]
            result = ', '.join(result)
        
        else: result = ''.join(result)

        return mark_safe(result) #self.measure or

    compiledSize = property(getCompiledSize)
    weight = models.FloatField(null=True, blank=True)
    article_family = models.ForeignKey(ArticleFamily)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.ref)

    def has_one_articleoption(self):
        if self.articleoption_set.count() == 1L:
            return True
        else:
            return False

    def get_priceRanges(self, role):
        prices = dict([(p.discountQty or 0, p) for p in self.pricing_set.filter(forRole__in = (role in HAS_RIGHTS and HAS_RIGHTS or NO_RIGHTS)).order_by('-forRole', 'discountQty')])
#        prices = dict([(p.discountQty or 0, p.price) for p in \
#                       self.pricing_set.filter(for_promotion__isnull = True).\
#                       filter(forRole__in = (role in HAS_RIGHTS and HAS_RIGHTS or NO_RIGHTS)).order_by('-forRole', 'discountQty')])
 
        
        return prices

    class Meta:
        db_table = 'apps_article'
        ordering = ['ref']

#===============================================================================
# class AODiscountGroup(models.Model):
#    name = CharField(max_length=255, unique=True)
#===============================================================================

class ArticleOption(models.Model):
    is_articleDB = True

    ref = models.CharField(max_length=16)
    quantity_stock = models.IntegerField(null=True, default=0)
    sub_image_code = models.CharField(max_length=48, null=True, blank=True) # ticket 43

    article = models.ForeignKey(Article)

    def __str__(self):
        return self.ref

    def has_image(self):
        return True

    def _getImgName(self):
        return "%s.jpg" % (self.sub_image_code and self.sub_image_code or self.ref)
    
    imgName = property(_getImgName)
    
    def _get_availability(self):
        return self.quantity_stock > 0
    available = property(_get_availability)
    class Meta:
        db_table = 'apps_articleoption'
        ordering = ['ref']

class Pricing(models.Model):
    is_articleDB = True

    _price = models.FloatField()
    _old_price = models.FloatField()
    
    def setPrice(self, value):
        self._price = round(value * 1000) / 1000

    def getPrice(self):
        if(self._price):
            return round(self._price * 100) / 100
        else:
            return self._price
    def setOldPrice(self, value):
        self._old_price = round(value * 1000) / 1000

    def getOldPrice(self):
        if(self._old_price):
            return round(self._old_price * 100) / 100
        else:
            return self._old_price
    price = property(getPrice, setPrice)
    old_price = property(getOldPrice, setOldPrice)
    discountQty = models.IntegerField(null=True, blank=True)
    forRole = models.CharField(max_length=1, choices=USER_GROUPS)
    tax_included = models.BooleanField(default = False)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    
    article = models.ForeignKey(Article)
    for_promotion = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return u'%s %s %s' % (str(self.article), str(self.forRole), str(self.price))

    class Meta:
        db_table = 'apps_pricing'
        ordering = ['article','-_price']

class LanguageManager(models.Manager):
    
    def get_from_cache(self, id):
        key = 'LP_%s' % id
        data = cache.get(key, False)
        if data:
            return data
        else:
            lp = self.get(pk=id)
            cache.set(key, lp, 600)
            return cache.get(key)

class LanguagePack(models.Model):
    '''
    LanguagePack used by DB i18n
    '''
    is_articleDB = True

    message_id = models.CharField(max_length=48, blank=True, null=True)

    en = models.CharField(max_length=255)
    de = models.CharField(blank=True, null=True, max_length=255)
    fr = models.CharField(blank=True, null=True, max_length=255)
    it = models.CharField(blank=True, null=True, max_length=255)
    pl = models.CharField(blank=True, null=True, max_length=255)
    es = models.CharField(blank=True, null=True, max_length=255)
    dk = models.CharField(blank=True, null=True, max_length=255)
    sw = models.CharField(blank=True, null=True, max_length=255)
    no = models.CharField(blank=True, null=True, max_length=255)
    ru = models.CharField(blank=True, null=True, max_length=255)
    gr = models.CharField(blank=True, null=True, max_length=255)
    nl = models.CharField(blank=True, null=True, max_length=255)
    ch = models.CharField(blank=True, null=True, max_length=255)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    objects = LanguageManager()

    def __str__(self):
        return '%s %s' % (self.__class__.__name__, self.en)

    class Meta:
        db_table = 'apps_languagepack'

class Order(models.Model):
    '''
    When user have confirmed his shopping data, an order will be created.
    Order can never be changed, so I store it into XML format.
    '''
#===============================================================================
# -2 - Error in Sending EMail
# -1 - deleted
#  0 - current shopping list
#  1 - ordered 
#  2 - synched to BOP
#===============================================================================
    status = models.IntegerField(default=0)

    user = models.ForeignKey(User)
    
    comment = models.TextField(null=True, blank = True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    ordered_in_shop = models.TextField(null=True, blank = True, default = settings.SHOP_NAME)
    #alter table devel.apps_order add column meta_data text;
    meta_data = JSONField(null=True, blank=True)



    def __unicode__(self):
        return u'<Order:%s, Status: %s>' % (self.id, self.status)

    class Meta:
        db_table = 'apps_order'

class OrderItem(models.Model):
    '''
    Each ShoppingItem represents a item in Shopping Cart or Saved list.
    Identified by field type.
    '''

    a_ref = models.CharField(max_length=32, db_index=True)
    ao_ref = models.CharField(max_length=16)
    qty = models.IntegerField(default=0)
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discountPrice = models.DecimalField(max_digits=10, decimal_places=2)
    discounted = models.BooleanField(default=False)
    discountQty = models.IntegerField(default=0)
    tax_included = models.BooleanField(default=False)
    description = models.TextField(null = True, blank = True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

#===============================================================================
# -1 - deleted
#  0 - current shopping list
#  1 - ordered 
#===============================================================================
    status = models.IntegerField(default=0)

    # ManyToOne -> ShoppingCart
    order = models.ForeignKey(Order)

    def __unicode__(self):
        return u'%s-%s: %spcs' % (self.a_ref, self.ao_ref, self.qty)

    class Meta:
        db_table = 'apps_orderitem'

