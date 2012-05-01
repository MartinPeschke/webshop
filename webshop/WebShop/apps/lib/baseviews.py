from django.http import HttpResponseRedirect
from django.views.generic.base import View, TemplateView, TemplateResponseMixin
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse_lazy
from django.contrib import auth, messages
from django.utils.translation import ugettext as _, ugettext_lazy

from WebShop.apps.user.lib import is_studio_user, is_in_signup

class HTTPRedirect(Exception):
    def __init__(self, url):
        self.url = url



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
            handler = getattr(self, "_"+request.method.lower(), self.http_method_not_allowed)
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
        if user.is_active:
            return super(BaseLoggedInView, self).dispatch(request, *args, **kwargs)
        elif not user.is_anonymous():
            messages.add_message(request, messages.ERROR, _('Anmeldung erforderlich!'))
            return HttpResponseRedirect(self.LOGIN_URL)
        elif is_in_signup(user):
            messages.add_message(request, messages.ERROR, _('Bitte Registrierung beenden!'))
            return HttpResponseRedirect(self.get_user_signup_details_url(request))
        elif not user.is_active:
            messages.add_message(request, messages.ERROR, _('Bitte zuerst Konto aktivieren beenden!'))
            return HttpResponseRedirect(self.HOME_URL)
        else:
            raise Exception("User is in unknown state!")





class BaseFormView(BaseView):
    def get(self, request, *args, **kwargs):
        return {'form' : self.form_cls()}
    def post(self, request, *args, **kwargs):
        _form = self.form_cls(request.POST)
        if not _form.is_valid():
            return {'form' : _form }
        else:
            result = self.on_success(request, _form.cleaned_data)
        return result

    def on_success(self, request, cleaned_data):
        pass