from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from WebShop.apps.contrib.cart import Cart
from WebShop.apps.contrib.decorator import json
from WebShop.apps.lib.baseviews import BaseLoggedInView
from WebShop.apps.order.models import Order

__author__ = 'Martin'


class ShoppingCartView(BaseLoggedInView):
    template_name = 'user/profile/shopping_cart.html'
    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', None)
        if not isinstance(cart, Cart):
            request.session['cart'] = Cart(request.user)
        return {'cart':cart}

class OrderHistoryView(BaseLoggedInView):
    template_name = 'user/profile/order_history.html'
    def get(self, request, *args, **kwargs):
        orders = Order.objects.select_related().filter(user = request.user, status_id__gt = 0).order_by('-create_time')
        return {'orders': orders}


@json
def add_to_cart(request):
	if request.method == 'GET':
		return HttpResponseNotAllowed(['GET'])

	items = request.POST.items()

	if 'cart' not in request.session:
		cart = Cart(request.user)
	else:
		cart = request.session['cart']
	was_added = cart.addToCart(items)
	request.session['cart'] = cart
	return {'cart_html':render_to_string('user/profile/cart_items.html', locals(), context_instance=RequestContext(request))}



def update_cart(request):
    if request.method == 'GET':
        return HttpResponseNotAllowed(['GET'])

    items = request.POST.items()
    cart = request.session['cart'] = Cart(request.user)
    cart.addToCart(items)

    return HttpResponseRedirect(reverse("cart-route"))

def delete_item(request, id):
    '''
     Used by delete button on shopping cart page
     '''
    cart = request.session.get('cart',None)
    if cart:
        cart.removeItem(id)
        request.session['cart'] = cart
    return HttpResponseRedirect(reverse("cart-route"))