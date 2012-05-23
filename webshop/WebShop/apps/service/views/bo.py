import sys, simplejson, bz2, base64, os

from django.http import *
from django.core.cache import cache

from django.db import  connection
from WebShop.apps.explore.models import Shop, Line, ArticleFamily, Promotion, Article, ArticleOption, Pricing, ArticleType
from WebShop.apps.user.models import Address, BankAccount, CreditCard, Profile
from WebShop.apps.order.models import Order, PaymentMethod
from django.contrib.auth.models import User
from WebShop.apps.contrib.decorator import _guard_bo, json_encode

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s]%(levelname)-8s"%(message)s"',
                    datefmt='%Y-%m-%d %a %H:%M:%S',
                    filename='bo_update.log',
                    filemode='a+')

@_guard_bo
def ping(request):
    cursor = connection.cursor()
    cursor.execute("SELECT max(id) FROM apps_order")
    row = cursor.fetchone()
    return HttpResponse(str(row[0]))
    
@_guard_bo
def getAllOrders(request):
    order_status = request.POST.get('order_status', None)
    from_id = request.POST.get('from_id', None)
    orders = Order.objects
    if order_status and order_status != u'None':
        orders = orders.filter(status = int(order_status))
    if from_id:
        orders = orders.filter(id__gt = from_id)

    orders = orders.all()
    for order in orders:
        order.items = order.orderitem_set.all()
        
        profile = order.user.get_profile()
        
        try:
            address = Address.objects.get(user=order.user, type__name='billing')
        except Address.DoesNotExist:
            address = None

        try:
            shipping = Address.objects.get(user=order.user, type__name='shipping')
        except Address.DoesNotExist:
            shipping = None

        try:
            bankaccount = BankAccount.objects.get(user=order.user)
        except BankAccount.DoesNotExist:
            bankaccount = None
        try:
            creditcard = CreditCard.objects.get(user=order.user)
        except CreditCard.DoesNotExist:
            creditcard = None
        
        order.user_email = order.user.email
        try:
            profile.verbose_payment_method = unicode(order.payment_method)
        except PaymentMethod.DoesNotExist:
            profile.verbose_payment_method = 'unknown'
        order.profile = profile
        order.address = address
        order.shipping = shipping
        order.bankaccount = bankaccount
        order.creditcard = creditcard
    return HttpResponse(json_encode(orders))

@_guard_bo
def customer_has_account(request):
    bo_customer_no = request.REQUEST.get('bo_customer_no', None)
    profile = None
    try:
        profile = Profile.objects.get(bo_customer_no = bo_customer_no)
    except Profile.DoesNotExist:
        profile = None
    except Profile.MultipleObjectsReturned:
        profile = None
    if(profile):
        return HttpResponse(profile.json)
    else: 
        return HttpResponse('null')

@_guard_bo
def all_customers(request):
    result = {'profiles':Profile.objects.all(), 'users': User.objects.all()}
    return HttpResponse(json_encode(result))

@_guard_bo
def quick_save_customer_data(request):
    profile_id = request.REQUEST.get('profile_id', None)
    bo_customer_no = request.REQUEST.get('bo_customer_no', None)
    try:
        p = Profile.objects.get(pk=profile_id)
    except Profile.DoesNotExist:
        raise Http404
    p.bo_customer_no = bo_customer_no 
    p.save()
    
    order_id = request.REQUEST.get('order_id', None)
    order_status = request.REQUEST.get('order_status', None)
    try:
        o = Order.objects.get(pk=order_id)
    except Order.DoesNotExist:
        raise Http404
    o.status = order_status
    o.save() 
    return HttpResponse(simplejson.dumps({'id':p.id, 'bo_customer_no':p.bo_customer_no}))

@_guard_bo
def save_customer_data(request):
    webuser_id = request.REQUEST.get('webuser_id', None)
    data = request.REQUEST.get('data', None)
    if(webuser_id):
        try:
            user = User.objects.get(pk = webuser_id)
        except User.DoesNotExist:
            user = None
        except User.MultipleObjectsReturned:
            user = None
    else:
        user = User()
        profile = Profile(user = user)
        shipping = Address(user = user, type='shipping')
        billing = Profile(user = user, type='billing')
        profile.user = user
        shipping.user = user
        billing.user = user
   
    user.get_profile().json = data  
    
    if(user):
        return HttpResponse(user.get_profile().json)

@_guard_bo
def backup_upload(request):
    fname = os.path.join(settings.DATA_ROOT, request.POST.get('fname', '').replace('bz2', 'sql'))
    content = str(request.POST.get('file'))

    f = open(fname, 'w')
    f.write(bz2.decompress(base64.urlsafe_b64decode(content)))
    f.close()

    cache.set('bo_update_fname', fname, 600000)
    fname = cache.get('bo_update_fname')
    
    return HttpResponse('[WEBSHOP] <b>%s</b> Backup Uploaded Successfully' % os.path.split(fname)[-1])


@_guard_bo
def backup_replay(request):
	fname = cache.get('bo_update_fname')
	db = settings.DATABASES['articledb']
	exec_cmd = 'mysql -u%s -p%s -e "source %s;" %s' % (db['USER'],db['PASSWORD'], fname.replace('\\','/'), db['NAME'])
	print exec_cmd
	exit_code = os.system(exec_cmd)
	if(exit_code):
		return HttpResponse('[WEBSHOP ERROR] Backup konnte nicht eingespielt werden')
	else:
		return HttpResponse('[WEBSHOP] <b>%s</b> Backup wurde eingespielt' % os.path.split(fname)[-1])

def _createPromotion(af, is_sale = False):
    promos = af.promotion_set.filter(is_sale = is_sale, is_active = True)

    if not promos:
        promo = Promotion(family=af, shop = af.line.shop, desc_I18N_id = af.desc_I18N_id,\
              logopath = af.logopath, is_sale = is_sale)
        promo.save()
    else:
        for p in promos:
            p.desc_I18N_id = af.desc_I18N_id
            logopath = af.logopath
            p.save()


def _removePromotion(af, is_sale = False):
    promos = af.promotion_set.filter(is_sale = is_sale)
    for p in promos:
        p.delete()


def parseJson(dobj = None):
    print 'trying to import json data'
    ao_count = 0
    for shopDict in dobj:
        shop_ref = shopDict["shop_ref"].lower()
        if(not shopDict["inWebshop"]):
            try:
                Shop.objects.get(ref=shop_ref).delete()
            except Shop.DoesNotExist:
                pass
        else:
            try:
                shop = Shop.objects.get(ref=shop_ref)
            except Shop.DoesNotExist:
                shop = Shop(ref=shop_ref)
                shop.name = shopDict.get('name',None)
                shop.logopath=shopDict.get('logopath',None)
                shop.viewableByRole = shopDict.get('webshop_viewableByRole', None)
                shop.save()

            for lineDict in shopDict.get('lines',[]):
                line_ref = lineDict["line_ref"]
                print 'processing line', line_ref
                if(not lineDict["inWebshop"]):
                    try:
                        Line.objects.get(ref=line_ref).delete()
                    except Line.DoesNotExist:
                        pass
                else:
                    try:
                        line = Line.objects.get(ref=line_ref)
                    except Line.DoesNotExist:
                        line = Line(ref=line_ref)

                        line.shop = shop
                        line.logopath=lineDict.get('logopath',line_ref)
                        line.name = lineDict.get('name',None)
                        line.viewableByRole = lineDict.get('webshop_viewableByRole', None)
                    # no line should have lower view privilege than its shop
                        if(line.viewableByRole < shop.viewableByRole):
                            line.viewableByRole = shop.viewableByRole
                        line.sort = lineDict.get('sortPos',None)
                        line.save()

                for atDict in lineDict.get('art_types',[]):
                    families = atDict.pop('families',[])
                    try:
                        at = line.articletype_set.get(en=atDict['en'])
                    except ArticleType.DoesNotExist:
                        at = ArticleType(line = line)
                    at.__dict__.update(atDict)
                    print 'processing', line.ref, atDict['en'], len(families), 'Families'
                    if(families): 
                        at.save()
                    else:
                        print 'no families in type <%s-%s>, proceeding with next type' % (line.ref, atDict['en'])

                    for afDict in families:
                        print afDict["af_ref"], afDict.get("inWebshop", False)
                        if(not afDict.get("inWebshop", False)):
                            try:
                                af = ArticleFamily.objects.get(ref=afDict["af_ref"])
                                _removePromotion(af, True)
                                _removePromotion(af, False)
                                af.delete()
                            except ArticleFamily.DoesNotExist:
                                pass
                        else:
                            try:
                                family = ArticleFamily.objects.get(ref=afDict["af_ref"])
                            except ArticleFamily.DoesNotExist:
                                family = ArticleFamily(ref=afDict["af_ref"])

                            family.body_part = afDict.get('body_part',None)
                            family.art_type_id = at.id
                            family.desc = afDict.get('desc',None)
                            family.logopath = afDict.get('logopath',family.logopath)
                            family.line = line
                            family.measure = afDict.get('measureUnit', 'mm')
                            family.save()
                            if(afDict.get('inWebshopNew',False)):
                                _createPromotion(family, is_sale = False)
                            else: 
                                _removePromotion(family, is_sale = False)
                            if(afDict.get('inWebshopSale',False)):
                                _createPromotion(family, is_sale = True)
                            else:
                                _removePromotion(family, is_sale = True)
        
                            for articleDict in afDict.get('articles',None):
                                try:
                                    article = Article.objects.get(ref=articleDict["a_ref"])
                                except Article.DoesNotExist:
                                    article = Article(ref=articleDict["a_ref"])

                                article.diameter_length = articleDict.get('diameter_len',None) or 0
                                article.ball_size1 = articleDict.get('ball_size1',None) or 0
                                article.ball_size2 = articleDict.get('ball_size2',None) or 0
                                article.thickness = articleDict.get('thickness',None) or 0
                                article.weight = articleDict.get('weight',None) or 0
                                article.article_family = family                                    
                                article.save()
        
                                for aoDict in articleDict.get('options',None):
                                    if(aoDict):
                                        try:
                                            option = ArticleOption.objects.get(article=article, ref=aoDict['ao_ref'])
                                        except ArticleOption.DoesNotExist:
                                            option = ArticleOption(article=article, ref=aoDict['ao_ref'])
                                        
                                        option.quantity_stock = aoDict.get('stockQty',None)
                                        option.sub_image_code = aoDict.get('subImgCode',None)
                                        option.save()
                                        ao_count+=1

                                for priceDict in articleDict.get('pricings',None):
                                    try:
                                        if not priceDict.get('discountQty', None):
                                            price_obj = Pricing.objects.filter(forRole=priceDict['cg_ref'],
                                                                            article=article, 
                                                                            discountQty__isnull = True)[0:1].get()
                                        else:
                                            price_obj = Pricing.objects.filter(forRole=priceDict['cg_ref'],
                                                                            article=article, 
                                                                            discountQty = priceDict.get('discountQty', None))[0:1].get()
                                    except Pricing.DoesNotExist:
                                        price_obj = Pricing(forRole=priceDict['cg_ref'],
                                                            article=article, 
                                                            discountQty = priceDict.get('discountQty', None))

                                    if(not priceDict.get('price', None)):
                                        if(price_obj.id):
                                            price_obj.delete()
                                    else:
                                        price_obj.price = float(priceDict.get('price', None))
                                        price_obj.save()
    return ao_count

def echo(request):
    '''echo BO push JSON, to update webshop DB content:
        - for debug ,just flush /services/echo/ will try usage local file apps/data.json.bz2 to update
        - for usage just flush BO://../pickling to push JSON here
        - todo:
            - responses all step msg back to BO
    '''    
    if request.POST:
        logging.info("received update DB POST request")
        try:
            data = bz2.decompress(base64.urlsafe_b64decode(request.POST['data']))
            user = request.POST['user']
            passwd = request.POST['passwd']
            print "User:", user, passwd
            dobj = sjson.JSONDecoder().decode(data)                
            ao_count = parseJson(dobj)
            logging.info("BO Database Update done...")
        except:
            print 'uncaught echo!', sys.exc_type, sys.exc_value            
            return HttpResponse('<div style="font-color:red;">Some Serious Error Occured!</div>')
        else: 
            return HttpResponse("<div style=\"width:80px\">[Webshop] Updated: <b>%s</b><br/> with<br/> <b>%s</b> ArticleOptions</div>" % 
                            (", ".join([str(shop["shop_ref"]) for shop in dobj]), ao_count))


def inWebShop(request):
    import simplejson
    article_families = [af.ref for af in ArticleFamily.objects.filter(shop_new=True)]
    lines = [(line.ref,line.sort) for line in Line.objects.all()]
    return HttpResponse(simplejson.dumps(dict(lines = lines, families = article_families)))

def index(request):
    title = "BackOffice agent::"
    # for default service action
    return HttpResponse(sjson.JSONEncoder().encode(__all__))

def ulImageLib(request):
    '''BO push b64encoded bz2 data, to update webshop ImgLib content:
    '''
    from WebShop.utils.ziputils import unzipToFolder
    import tempfile
    if request.POST:
        print 'received request'
        logging.info("[bebug]::received update ImgLib POST request")
        try:
            print request.POST['data'][:60]
            data = base64.urlsafe_b64decode(request.POST['data'])
            target = os.path.join(settings.MEDIA_ROOT, 'files')
            tf = tempfile.TemporaryFile()
            tf.write(data)
            unzipToFolder(target, tf)
        except:            # all uncaught exceptions come here
            print 'uncaught ulImageLib!', sys.exc_type, sys.exc_value            
        return HttpResponse("[webshop] Updated Webshop ImgLib")
    