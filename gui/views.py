from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import HttpResponse
from forms import LoginForm, SubscriberForm, AttributeUpdateForm, AttributeCreateForm
from helpers import handle_ldap_errors, handle_credentials_errors, LdapHandler
from django.http import QueryDict
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
            return HttpResponse(json.dumps({'success': False, 'validation_error': True, 'message': form.errors,
                                            'form_error': True}),
                                content_type="application/json", status=200)

        with LdapHandler(form.cleaned_data['host_address'], form.cleaned_data['port_number'],
                         form.cleaned_data['username'], form.cleaned_data['password'],
                         form.cleaned_data['scope_subtree']):
            request.session['username'] = form.cleaned_data['username']
            request.session['password'] = form.cleaned_data['password']
            request.session['host_address'] = form.cleaned_data['host_address']
            request.session['port_number'] = form.cleaned_data['port_number']
            request.session['scope_subtree'] = form.cleaned_data['scope_subtree']

        return HttpResponse(json.dumps({'success': True}), content_type='application/json', status=200)

    def delete(self, request, *args, **kwargs):
        request.session.flush()
        return HttpResponse(json.dumps({'success': True}), content_type='application/json', status=200)


class SubscriberView(View):
    @handle_ldap_errors
    @handle_credentials_errors
    def get(self, request, *args, **kwargs):
        form = SubscriberForm(request.GET)
        if not form.is_valid():
            return HttpResponse(
                json.dumps({'success': False, 'validation_error': True, 'message': form.errors, 'form_error': True}),
                content_type="application/json", status=200)

        with LdapHandler(request.session['host_address'], request.session['port_number'], request.session['username'],
                         request.session['password'], request.session['scope_subtree']) as ldap_handler:
            profiles = ldap_handler.search(form.cleaned_data['subscriber_id'])
            return HttpResponse(json.dumps({'success': True, 'profiles': profiles}), content_type="application/json",
                                status=200)


class ProfileAttributeView(View):
    def _change_ldap_profile(self, request, subscriber_id, attributes, not_allowed_msg):
        try:
            with LdapHandler(request.session['host_address'], request.session['port_number'],
                             request.session['username'], request.session['password'],
                             request.session['scope_subtree']) as ldap_handler:
                ldap_handler.change_profile(subscriber_id, attributes)

        except (ldap.NOT_ALLOWED_ON_RDN, ldap.OBJECT_CLASS_VIOLATION):
            return HttpResponse(json.dumps({'success': False, 'message': not_allowed_msg}),
                                content_type="application/json", status=200)

        return HttpResponse(json.dumps({'success': True}), content_type="application/json", status=200)


    @handle_ldap_errors
    @handle_credentials_errors
    def delete(self, request, *args, **kwargs):
        attributes = [(ldap.MOD_DELETE, kwargs['attribute'], [])]
        return self._change_ldap_profile(request, kwargs['subscriber_id'], attributes,
                                         "Attribute deletion is not allowed")


    @handle_ldap_errors
    @handle_credentials_errors
    def put(self, request, *args, **kwargs):
        params = QueryDict(request.body)
        form = AttributeUpdateForm(params)
        if not form.is_valid():
            return HttpResponse(
                json.dumps({'success': False, 'validation_error': True, 'message': form.errors, 'form_error': True}),
                content_type="application/json", status=200)

        attributes = [
            (ldap.MOD_REPLACE, kwargs['attribute'], [form.cleaned_data['attribute_val'].encode('utf-8').strip()])]
        return self._change_ldap_profile(request, kwargs['subscriber_id'], attributes,
                                         "Attribute updating is not allowed")


class ProfileAttributeCreateView(View):
    @handle_ldap_errors
    @handle_credentials_errors
    def post(self, request, *args, **kwargs):
        form = AttributeCreateForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                json.dumps({'success': False, 'validation_error': True, 'message': form.errors, 'form_error': True}),
                content_type="application/json", status=200)

        attributes = [(ldap.MOD_ADD, form.cleaned_data['attribute_key'], form.cleaned_data['attribute_val'])]
        try:
            with LdapHandler(request.session['host_address'], request.session['port_number'],
                             request.session['username'], request.session['password'],
                             request.session['scope_subtree']) as ldap_handler:
                ldap_handler.add_attribute(form.cleaned_data['dn'], attributes)

        except (ldap.NOT_ALLOWED_ON_RDN, ldap.OBJECT_CLASS_VIOLATION):
            return HttpResponse(json.dumps({'success': False, 'message': "Attribute adding is not allowed"}),
                                content_type="application/json", status=200)

        return HttpResponse(json.dumps({'success': True}), content_type="application/json", status=200)

