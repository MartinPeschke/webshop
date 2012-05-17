from decimal import Decimal, ROUND_UP
from operator import attrgetter

from WebShop.apps.user.lib import get_role
from WebShop.apps.user.user_roles import simple_role
from WebShop.apps.explore.models import ArticleOption, Pricing
from django.conf import settings

class Cart(object):
    items = []
    taxRate = settings.TAX_RATE
    total = Decimal('0.0').quantize(Decimal('.01'), rounding=ROUND_UP)
    simple_user_role = None

    def __init__(self, user):
        self.initUser(user)

    def initUser(self, user):
        self.simple_user_role = simple_role[get_role(user)]
        if(user.is_authenticated() and user.get_profile().taxFreed):
            self.taxRate = 0
        self.total = 0
        items = [(ao.id, ao.quantity) for ao in self.items]
        self.items = []
        if items: self.addToCart(items)

    def _get_tax(self, role = 'K'):
        tax = Decimal('0.0').quantize(Decimal('.01'), rounding=ROUND_UP)
        if role == 'E':
            tax = (self.total - self.total / Decimal("%.2f" % (self.taxRate/100 + 1))).quantize(Decimal('.01'), rounding=ROUND_UP)
        else:
            tax = (self.total * Decimal("%.2f" % (self.taxRate/100))).quantize(Decimal('.01'), rounding=ROUND_UP)
        return tax
    tax = property(_get_tax)
    def tax_E(self):
         return self._get_tax('E')

    def _get_all_total(self, role='K'):
        all_total = Decimal('0.0').quantize(Decimal('.01'), rounding=ROUND_UP)
        if role == 'E':
            all_total = self.total
        else:
            all_total = (self.total + self.tax).quantize(Decimal('.01'), rounding=ROUND_UP)
        return all_total
    all_total = property(_get_all_total)
    def all_total_E(self):
        return self._get_all_total('E')

    def removeItem(self, id):
        id = int(id)
        item = self._get_ItemDict().get(id,None)
        self.items = [item for item in self.items if item.id != id]
        self.refreshPricings()
        return item

    def _get_ItemDict(self):
        return dict([(ao.id, ao) for ao in self.items])


    def refreshPricings(self):
        #getting article quantities & prices
        article_qty_map = {}
        for item in self.items:
            article_qty_map[item.article_id] = article_qty_map.setdefault(item.article_id, 0) + item.quantity
        pricings = Pricing.objects.get_article_prices(article_qty_map, self.simple_user_role)

        #updating cart items with correct price
        self.total = 0
        for item in self.items:
            pricing = pricings.get(item.article_id, None)
            if pricing:
                item.price, item.discountQty, item.discounted, item.tax_included =\
                pricing.price, pricing.discountQty, pricing.is_discounted, pricing.tax_included
                item.total = Decimal('%s' % (item.price * item.quantity)).quantize(Decimal('.01'), rounding=ROUND_UP)
                self.total += item.total
        self.items.sort(key = lambda x: (x.article.ref, x.ref))
        return True


#===============================================================================
#    discount preis nicht ueber optionen 
#===============================================================================
    def addToCart(self, itemQtyList):
        items = self._get_ItemDict()

        # adding items to cart
        for id, qty in itemQtyList:
            id, qty = (int(id), int(qty))
            if qty:
                ao = items.setdefault(id, ArticleOption.objects.get(pk=id))
                ao.quantity = getattr(ao, 'quantity', 0) + qty
                if ao.quantity <= 0:
                    items.pop(id)
        self.items = items.values()
        return self.refreshPricings()

    def _serialize(self):
        result = []
        for item in self.items:
            result.append({'a_ref':item.article.ref,
                        'ao_ref':item.ref,
                        'qty':item.quantity,
                        'totalPrice':item.total,
                        'price': Decimal('%s' % item.price).quantize(Decimal('.01'), rounding=ROUND_UP),
                        'tax_included': item.tax_included,
                        'discounted': item.discounted,
                        'discountQty': item.discountQty})
        return result
