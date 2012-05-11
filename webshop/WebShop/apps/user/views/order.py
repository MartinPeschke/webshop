from django.core.urlresolvers import reverse
import simplejson
from operator import itemgetter, add
from decimal import Decimal, ROUND_UP

from django.shortcuts import render_to_response
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect, HttpResponseNotAllowed

from django.conf  import settings
from WebShop.apps.lib.baseviews import BaseFormView, BaseLoggedInView, HTTPRedirect
from WebShop.apps.user.models.creditcard import CreditCard
from WebShop.apps.user.models.bank_account import BankAccount
from WebShop.apps.user.forms import PaymentFormRetail, PaymentFormWholesale, CreditCardForm, BankAccountForm
from WebShop.apps.user.user_roles import HAS_RIGHTS
from WebShop.apps.user.views import profile

import WebShop.utils.mail as mail
from WebShop.apps.contrib.cart import Cart
from WebShop.apps.user.models import OrderItem, Order
from WebShop.apps.user.views.profile import _get_user_data


def _get_current_cid(request):
	cids = sorted(request.session.get('cid_list') or [], key = itemgetter('timestamp'), reverse = True)
	cid_candidate = ''
	if cids and isinstance(cids[0], dict):
		cid_candidate = cids[0].get('cid', '') or ''
	return cid_candidate

class CheckoutView(BaseLoggedInView):
    template_name = 'user/order/payment.html'
    def pre_validate(self, request, *args, **kwargs):
        if not request.session.get('cart',None):
            raise HTTPRedirect(self.LOGIN_URL)

def checkout(request):
    errors = []
    payment_method = profile.payment_method or 'Transfer'

    try:
        cc = CreditCard.objects.get(user=request.user)
        dictCC = {'ccNumber':cc.ccNumber}
        dictCC.update(cc.__dict__)
        card_form = CreditCardForm(dictCC)
        card_form.ccNumber = cc.ccNumber

    except CreditCard.DoesNotExist:
        card_form = CreditCardForm({'owner':'%s %s' % (profile.first_name, profile.last_name)})

    try:
        bank_form = BankAccountForm(BankAccount.objects.get(user=request.user).__dict__)
    except BankAccount.DoesNotExist:
        bank_form = BankAccountForm({'owner':'%s %s' % (profile.first_name, profile.last_name)})

    if(profile.role in HAS_RIGHTS):
        payment_form = PaymentFormWholesale({'payment_method': payment_method})
    else:
        payment_form = PaymentFormRetail({'payment_method': payment_method})


    cid_candidate = _get_current_cid(request)
    return render_to_response('', locals(), context_instance=RequestContext(request))


def confirm_address(request):
	if(not request.user.is_authenticated() or not request.session.get('cart',None)):
		return HttpResponseRedirect('/user/login/?forward_URL=/user/shopping_cart/confirm/')
	user, profile, billing, shipping = _get_user_data(request.user)
	try:
		weekdays = simplejson.loads(profile.weekdays)
	except ValueError, e:
		# only needed until all profiles are converted to json
		try:
			weekdays = eval(profile.weekdays)
		except:
			weekdays = None
		profile.weekdays = simplejson.dumps(weekdays)
		profile.save()

	values = profile.__dict__
	values.update({'weekdays':weekdays, 'same_address': profile.same_address and 'Y' or 'N'})
	account_form = AccountForm(values)

	values = dict(map(lambda (k,v): ('billing-%s'%k, v), billing.__dict__.iteritems()))
	billing_form = AddressForm(values, prefix='billing')
	values = dict(map(lambda (k,v): ('shipping-%s'%k, v), shipping.__dict__.iteritems()))
	shipping_form = ShippingForm(values, prefix='shipping')

	if(profile.role in HAS_RIGHTS):
		return render_to_response('user/confirm_account_E.html', locals(), context_instance=RequestContext(request))
	else:
		return render_to_response('user/confirm_account_E.html', locals(), context_instance=RequestContext(request))




def process_order(request):
	if request.method == 'GET':
		return HttpResponseNotAllowed(['GET'])

	if not request.user.is_authenticated():
		return HttpResponseRedirect('/user/login/?return=/user/shopping_cart/')

	cid_candidate = _get_current_cid(request)

	profile = request.user.get_profile()
	payment_form = PaymentFormWholesale(request.POST.copy())
	card_form = CreditCardForm(request.POST.copy())
	bank_form = BankAccountForm(request.POST.copy())
	payment_method = payment_form.data['payment_method']
	if payment_form.is_valid():
		profile.payment_method = payment_form.cleaned_data['payment_method']
		profile.save()
		
		if payment_form.cleaned_data['payment_method'] == 'Credit':
			if(card_form.is_valid() and card_form.cleaned_data['ccNumber']):
				card, created = CreditCard.objects.get_or_create(user=request.user)
				card.owner = card_form.cleaned_data['owner']
				if('xxxx' not in card_form.cleaned_data['ccNumber']):
					card.ccNumber = card_form.cleaned_data['ccNumber']
				card.ctype = card_form.cleaned_data['ctype']
				card.valid_until = card_form.cleaned_data['valid_until']
				card.security_number = card_form.cleaned_data['security_number']
				card.save()
			else:
				return render_to_response('user/order/payment.html', locals(), context_instance=RequestContext(request))

		if payment_form.cleaned_data['payment_method'] == 'Direct':
			if(bank_form.is_valid() and bank_form.cleaned_data['accountno']):
				account, created = BankAccount.objects.get_or_create(user=request.user)
				account.owner = bank_form.cleaned_data['owner']
				account.accountno = bank_form.cleaned_data['accountno']
				account.blz = bank_form.cleaned_data['blz']
				account.bank_name = bank_form.cleaned_data['bank_name']
				account.save()
			else:
				return render_to_response('user/order/payment.html', locals(), context_instance=RequestContext(request))            
		order = send_order(request)
		order_total = reduce(add, [0] + [item.totalPrice for item in order.orderitem_set.all()])
		return render_to_response('user/order/complete.html', locals(), context_instance=RequestContext(request))
	else:
		order_comment = request.POST.get('order_comment', None)
		return render_to_response('user/order/payment.html', locals(), context_instance=RequestContext(request))

#===============================================================================
# def _jsonify_order(user, cart):
#    return DjangoJSONEncoder({'user':None, 'order':cart._serialize()})
#===============================================================================

def send_order(request): 
	cart = request.session.get('cart', None)
	if(cart):
		order = Order(user=request.user)
		order.comment = request.POST.get('order_comment', None)
		order.meta_data = {'cid_list' : request.session.get('cid_list', None),
						   'aktionscode':request.POST.get('cid')}
		order.save()
		if 'cid_list' in request.session: 
			del request.session['cid_list']
		if 'aktionscode' in request.session: 
			del request.session['aktionscode']

		for item in cart.items:
			oi = OrderItem(order = order, a_ref = item.article.ref, ao_ref = item.ref, 
						qty = item.quantity, totalPrice=item.total,
						price = Decimal('%s' % item.price).quantize(Decimal('.01'), rounding=ROUND_UP),
						discountPrice = Decimal('%s' % item.discountPrice).quantize(Decimal('.01'), rounding=ROUND_UP),
						discounted = item.discounted, discountQty = item.discountQty,
						tax_included = item.tax_included,
						description = getattr(item.article.article_family.desc, 'de') or getattr(item.article.article_family.desc, 'en'))
			oi.save()
		
		user, profile, billing, shipping = _get_user_data(request.user)
		c = Context({'user': user,
			'profile': profile,
			'cart':cart, 'order':order})

		try:
			card = CreditCard.objects.get(user=request.user)
			c['credit_card'] = card
		except CreditCard.DoesNotExist:
			pass
		try:
			ba = BankAccount.objects.get(user=request.user)
			c['bank_account'] = ba
		except BankAccount.DoesNotExist:
			pass

		try:
			order_html = mail.create_mail("%s Order" % settings.EMAIL_SUBJECT_PREFIX, settings.SERVER_EMAIL, settings.ORDER_MAIL, 'orderToBackoffice', c)
		except:
			order.status = -2
			order.save()
			raise
		else:
			order.status = 1
			order.save()
		del request.session['cart']
		return order