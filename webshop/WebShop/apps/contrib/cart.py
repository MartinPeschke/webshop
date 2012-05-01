from decimal import Decimal, ROUND_UP

from WebShop.apps.user.lib import get_role
from WebShop.apps.user.user_roles import simple_role
from WebShop.apps.explore.models import ArticleOption, Pricing
from django.conf import settings

class Cart(object):
	items = []
	taxRate = settings.TAX_RATE
	total = Decimal('0.0').quantize(Decimal('.01'), rounding=ROUND_UP)
	user_role = None

	def __init__(self, user, items = []):
		self.initUser(user)
		if(items):
			self.addToCart(items)

	def initUser(self, user):
		self.user_role = simple_role[get_role(user)]
		if(user.is_authenticated() and user.get_profile().taxFreed):
			self.taxRate = 0       
		self.total = 0
		items = [(ao.id, ao.quantity) for ao in self.items]
		self.items = []
		self.addToCart(items)

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
		try:
			self.total -= item.total
			del self.items[self.items.index(item)]
			self._calculateTotals()
		except:
			print 'No Item in Cart for Item:%s, could not delete!' % id
		return item

	def _get_ItemDict(self):
		return dict([(ao.id, ao) for ao in self.items])

    

#===============================================================================
#    discount preis nicht ueber optionen 
#===============================================================================
	def addToCart(self, itemQtyList):
		os = itemQtyList
		os.sort()
		items = self._get_ItemDict()
		
		
		added_items = []
		for id, qty in [(int(k),int(v)) for k,v, in os if int(v or 0)]:
			ao = items.get(id, ArticleOption.objects.get(pk=id))
			pRanges = ao.article.get_priceRanges(self.user_role)
			if(not pRanges):
				print 'No Pricings for Customer Role!'
			else:
				ao.quantity = getattr(ao, 'quantity', 0) + qty
				all_of_article = [item for item in items.values() if item.article_id == ao.article_id] + [ao]
				total_qty = sum(map(lambda x: x.quantity, all_of_article))
			
				ao.discounted = False
				pricing = pRanges.pop(0,Pricing(price=0.0, discountQty=0,forRole=self.user_role, tax_included=False))
				ao.discountQty, ao.discountPrice = (0,0)
				if pricing:
					ao.price =  Decimal(str(pricing.price)).quantize(Decimal('.01'), rounding=ROUND_UP)
				else:
					ao.price = 0.0
				ao.tax_included =  pricing.tax_included
				try:
					nextPricing = pRanges.popitem()
					ao.discountPrice = nextPricing[1].price
					ao.discountQty = nextPricing[1].discountQty
				except KeyError:
					ao.discount =''
				else:
					ao.discount = '<span class="discount_box"><span>%s</span>+</span> <span>%.2f</span>&euro;' % (ao.discountQty, ao.discountPrice)                    

				for item in all_of_article:
					item.total_qty = total_qty
					item.discounted = ao.discounted                 
					if ao.discountQty and total_qty >= ao.discountQty:
						item.discounted = True
						item.total = Decimal('%s' % (ao.discountPrice * item.quantity)).quantize(Decimal('.01'), rounding=ROUND_UP)
					else:
						item.total = Decimal('%s' % (ao.price * item.quantity)).quantize(Decimal('.01'), rounding=ROUND_UP)
				self.total += ao.total
				items[id] = ao
				
				added_items.append((ao.id, ao.quantity))

		self.items = items.values()
		self.items.sort(key = lambda x: (x.article.ref, x.ref))
		return added_items

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
