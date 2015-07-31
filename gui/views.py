from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import HttpResponse
from forms import LoginForm, SubscriberForm
from helpers import handle_ldap_errors
import json
import ldap


class HomePageView(TemplateView):

    template_name = "show.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        return context


class LoginView(View):
    @handle_ldap_errors
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if not form.is_valid():
            return HttpResponse(json.dumps({'success': False, 'validation_error': True, 'message': form.errors}), content_type="application/json", status=200)

        connection = ldap.initialize('ldap://127.0.0.1:389')
        connection.simple_bind_s(form.cleaned_data['username'], form.cleaned_data['password'])
        request.session['credentials'] = form.cleaned_data['username'], form.cleaned_data['password']
        connection.unbind_s()
        return HttpResponse(json.dumps({'success': True}), content_type='application/json', status=200)


class SubscriberView(View):
    @handle_ldap_errors
    def get(self, request, *args, **kwargs):
        form = SubscriberForm(request.GET)
        if not form.is_valid():
            return HttpResponse(json.dumps({'success': False, 'validation_error': True, 'message': form.errors}), content_type="application/json", status=200)

        username, password = request.session['credentials']
        connection = ldap.initialize('ldap://127.0.0.1:389')
        connection.simple_bind_s(username, password)
        ldap_profiles = connection.search_s('o=TE Data,c=EG', ldap.SCOPE_SUBTREE, '(uid=%s)' % form.cleaned_data['subscriber_id'])
        dictified = {}
        for profile in ldap_profiles:
            dictified[profile[0]] = profile[1]

        return HttpResponse(json.dumps({'success': True, 'profiles': dictified}), content_type="application/json", status=200)

