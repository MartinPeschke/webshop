from django.forms import Form
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.views.generic.base import View, TemplateResponseMixin
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext as _
import json

from webshop.apps.user.lib import is_studio_user, is_in_signup


class HTTPRedirect(Exception):
    def __init__(self, url):
        self.url = url


class BaseForm(Form):
    def addRules(self, rules):
        return rules

    def getRules(self):
        rules = {f.name: {"required": True} for f in self if f.field.required == True}
        return mark_safe(json.dumps(self.addRules(rules)))


class BaseView(TemplateResponseMixin, View):
    HOME_URL = reverse_lazy('home-route')
    LOGIN_URL = reverse_lazy('login-route')
    SIGNUP_URL = reverse_lazy('signup-route')
    SIGNUP_RETAIL_DETAILS_URL = reverse_lazy('signup-retail-details-route')
    SIGNUP_WHOLESALE_DETAILS_URL = reverse_lazy('signup-wholesale-details-route')

    def get_user_signup_details_url(self, request):
        if is_studio_user(request.user):
            return self.SIGNUP_WHOLESALE_DETAILS_URL
        else:
            return self.SIGNUP_RETAIL_DETAILS_URL

    def pre_validate(self, request, *args, **kwargs):
        pass

    def dispatch(self, request, *args, **kwargs):
        try:
            self.pre_validate(request, *args, **kwargs)
        except HTTPRedirect, r:
            return HttpResponseRedirect(r.url)

        if request.method.lower() in self.http_method_names:
            handler = getattr(self, "_" + request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        self.request = request
        self.args = args
        self.kwargs = kwargs
        try:
            return handler(request, *args, **kwargs)
        except HTTPRedirect, r:
            return HttpResponseRedirect(r.url)

    def _get(self, request, *args, **kwargs):
        template_context = self.get(request, *args, **kwargs)
        return self.render(request, template_context)

    def get(self, request, *args, **kwargs):
        pass

    def _post(self, request, *args, **kwargs):
        template_context = self.post(request, *args, **kwargs)
        return self.render(request, template_context)

    def post(self, request, *args, **kwargs):
        pass

    def render(self, request, template_context):
        return TemplateResponse(request, self.template_name, template_context)


class BaseLoggedInView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_anonymous():
            messages.add_message(request, messages.ERROR, _('Anmeldung erforderlich!'))
            return HttpResponseRedirect("{}?furl={}".format(self.LOGIN_URL, request.path))
        elif is_in_signup(user):
            messages.add_message(request, messages.ERROR, _('Bitte Registrierung beenden!'))
            return HttpResponseRedirect(self.get_user_signup_details_url(request))
        elif user.is_active:
            return super(BaseLoggedInView, self).dispatch(request, *args, **kwargs)
        else:
            messages.add_message(request, messages.ERROR, _('Bitte zuerst Konto aktivieren!'))
            return HttpResponseRedirect(self.HOME_URL)


class BaseFormView(BaseView):
    form = None

    def get(self, request, *args, **kwargs):
        return {'form': self.get_form_instance(request, *args, **kwargs)}

    def post(self, request, *args, **kwargs):
        _form = self.form = self.get_validation_form_instance(request)
        if not _form.is_valid():
            return {'form': _form}
        else:
            result = self.on_success(request, _form.cleaned_data)
        return result

    def get_form_instance(self, request, *args, **kwargs):
        return self.form_cls()

    def get_validation_form_instance(self, request):
        return self.form_cls(request.POST)

    def on_success(self, request, cleaned_data):
        pass
