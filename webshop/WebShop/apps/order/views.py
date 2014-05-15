from django.core.urlresolvers import reverse
from operator import itemgetter
from decimal import Decimal, ROUND_UP
from django.template.context import RequestContext
from django.utils.translation import ugettext as _, ugettext_lazy
from django.utils.safestring import mark_safe
from django.template import Context
from django.contrib import messages
from django.conf  import settings

from WebShop.apps.lib.baseviews import BaseFormView, BaseLoggedInView, HTTPRedirect
from WebShop.apps.order.models import OrderItem
from .forms import PaymentMethodForm, CreditCardForm, BankAccountForm
from .models import CreditCard, BankAccount, Order, PaymentMethod

import WebShop.utils.mail as mail
from WebShop.apps.user.views.profile import _get_user_data, BaseAccountAddressView

import simplejson

def _get_current_cid(request):
    cids = sorted(request.session.get('cid_list') or [], key = itemgetter('timestamp'), reverse = True)
    cid_candidate = ''
    if cids and isinstance(cids[0], dict):
        cid_candidate = cids[0].get('cid', '') or ''
    return cid_candidate


class ConfirmAddressView(BaseAccountAddressView):
    template_name = 'user/order/addresses.html'
    def on_success(self, request, cleaned_data):
        try:
            return super(ConfirmAddressView, self).on_success(request, cleaned_data)
        except HTTPRedirect:
            raise HTTPRedirect(reverse("checkout-route"))




class CheckoutView(BaseLoggedInView, BaseFormView):
    template_name = 'user/order/payment.html'
    form_cls = PaymentMethodForm
    def pre_validate(self, request, *args, **kwargs):
        if not request.session.get('cart',None):
            raise HTTPRedirect(self.LOGIN_URL)
        user, profile, billing, shipping = _get_user_data(request.user)
        if billing is None or shipping is None:
            messages.add_message(request, messages.ERROR, _('Bitte gib erst eine Liefer- und Rechnungsadresse an!'))
            raise HTTPRedirect(reverse('confirm-address-route'))

    def get_form_instance(self, request, *args, **kwargs):
        role = request.user.get_profile().role
        try:
            form =  self.form_cls(role,
                initial = {"payment_method": request.user.get_profile().preferred_payment_method}
            )
        except PaymentMethod.DoesNotExist:
            form =  self.form_cls(role,
                initial = {"payment_method": PaymentMethod.objects.filter_by_role(role)[0]}
            )
        return form

    def get(self, request, *args, **kwargs):
        role = request.user.get_profile().role
        return {'form' : self.get_form_instance(request, *args, **kwargs),
                'bankaccount_form': BankAccountForm(user = request.user),
                'creditcard_form': CreditCardForm(user = request.user),
                'available_methods': mark_safe(simplejson.dumps({p.id: p.name for p in PaymentMethod.objects.filter_by_role(role)}))
        }
    def post(self, request, *args, **kwargs):
        role = request.user.get_profile().role
        _form = self.form = self.form_cls(role, request.POST)
        if not _form.is_valid():
            return {'form' : _form,
                    'bankaccount_form': BankAccountForm(user = request.user),
                    'creditcard_form': CreditCardForm(user = request.user),
                    'available_methods': mark_safe(simplejson.dumps({p.id: p.name for p in PaymentMethod.objects.filter_by_role(role)}))
            }
        else:
            method = self.form.cleaned_data['payment_method'].name
            if method == 'CREDITCARD':
                secondary_form = CreditCardForm(None, request.POST)
            elif method == 'DIRECT_DEBIT':
                secondary_form = BankAccountForm(None, request.POST)
            else:
                secondary_form = None
            if secondary_form:
                if secondary_form.is_valid():
                    secondary_form.save(request.user)
                    result = self.on_success(request, _form.cleaned_data)
                else:
                    return {'form' : _form,
                            'bankaccount_form': BankAccountForm(None, request.POST),
                            'creditcard_form': CreditCardForm(None, request.POST),
                            'available_methods': mark_safe(simplejson.dumps({p.id: p.name for p in PaymentMethod.objects.filter_by_role(role)}))
                    }
            else:
                result = self.on_success(request, _form.cleaned_data)
        return result

    def on_success(self, request, cleaned_data):
        cart = request.session.get('cart', None)
        if cart:
            order = Order(user=request.user)
            order.comment = cleaned_data['payment_comment']
            order.payment_method = cleaned_data['payment_method']
            order.status_id = 0
            order.meta_data = {'cid_list' : request.session.get('cid_list', None),
                               'aktionscode':request.POST.get('cid')}
            order.save()
            profile = request.user.get_profile()
            profile.preferred_payment_method = cleaned_data['payment_method']
            profile.save()

            if 'cid_list' in request.session:
                del request.session['cid_list']
            if 'aktionscode' in request.session:
                del request.session['aktionscode']

            for item in cart.items:
                oi = OrderItem(
                    order = order,
                    a_ref = item.article.ref,
                    ao_ref = item.ref,
                    qty = item.quantity,
                    totalPrice=item.total,
                    price = Decimal('%s' % item.price).quantize(Decimal('.01'), rounding=ROUND_UP),
                    discounted = item.discounted,
                    discountQty = item.discountQty,
                    tax_included = item.tax_included,
                    description = getattr(item.article.article_family.desc, 'de') or getattr(item.article.article_family.desc, 'en'))
                oi.save()

            user, profile, billing, shipping = _get_user_data(request.user)

            c = RequestContext(request)
            c.update({'user': user
                         , 'profile': profile
                         , 'cart':cart
                         , 'order':order
                         , 'billing_address' : billing
                         , 'shipping_address' : shipping})

            cards = CreditCard.objects.filter(user=request.user).order_by('-id')
            if len(cards):
                c['credit_card'] = cards[0]
            ba = BankAccount.objects.filter(user=request.user).order_by('-id')
            if len(ba):
                c['bank_account'] = ba[0]
            try:
                mail.create_mail("%s Order" % settings.EMAIL_SUBJECT_PREFIX, settings.SERVER_EMAIL, settings.ORDER_MAIL, 'orderToBackoffice', c)
                mail.create_mail(_("Vielen Dank fuer Deine Bestellung bei Per-4"), settings.SERVER_EMAIL, user.email, 'order_confirmation', c)
            except:
                order.status_id = -2
                order.save()
                raise
            else:
                order.status_id = 1
                order.save()
        del request.session['cart']
        raise HTTPRedirect(reverse("order-success-route"))

class OrderSuccessView(BaseLoggedInView):
    template_name = 'user/order/success.html'