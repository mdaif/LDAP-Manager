from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import HttpResponse
from forms import LoginForm, SubscriberForm
from helpers import handle_ldap_errors, handle_credentials_errors
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
            return HttpResponse(json.dumps({'success': False, 'validation_error': True, 'message': form.errors}),
                                content_type="application/json", status=200)

        connection = ldap.initialize('ldap://{0}:{1}'.format(form.cleaned_data['host_address'],
                                                             form.cleaned_data['port_number']))
        connection.simple_bind_s(form.cleaned_data['username'], form.cleaned_data['password'])
        request.session['credentials'] = form.cleaned_data['username'], form.cleaned_data['password']
        request.session['host_address'] = form.cleaned_data['host_address']
        request.session['port_number'] = form.cleaned_data['port_number']
        connection.unbind_s()
        return HttpResponse(json.dumps({'success': True}), content_type='application/json', status=200)

    @handle_ldap_errors
    def delete(self, request, *args, **kwargs):
        del request.session['credentials']
        del request.session['host_address']
        del request.session['port_number']
        request.session.flush()
        response = HttpResponse(json.dumps({'success': True}), content_type='application/json', status=200)

        return response

class SubscriberView(View):
    @handle_ldap_errors
    @handle_credentials_errors
    def get(self, request, *args, **kwargs):
        form = SubscriberForm(request.GET)
        if not form.is_valid():
            return HttpResponse(json.dumps({'success': False, 'validation_error': True, 'message': form.errors}),
                                content_type="application/json", status=200)

        username, password = request.session['credentials']
        connection = ldap.initialize('ldap://{0}:{1}'.format(request.session['host_address'],
                                                             request.session['port_number']))
        connection.simple_bind_s(username, password)
        ldap_profiles = connection.search_s('o=TE Data,c=EG', ldap.SCOPE_SUBTREE,
                                            '(uid=%s)' % form.cleaned_data['subscriber_id'])
        connection.unbind_s()
        dictified = {profile[0]: profile[1] for profile in ldap_profiles}
        return HttpResponse(json.dumps({'success': True, 'profiles': dictified}), content_type="application/json",
                            status=200)


class ProfileAttributeView(View):
    def _change_ldap_profile(self, request, subscriber_id, mod_attrs, not_allowed_msg):
        dn = "uid={0}, ou=tedata.net.eg,ou=corporate,ou=email,o=TE Data,c=eg".format(subscriber_id)
        connection = ldap.initialize('ldap://{0}:{1}'.format(request.session['host_address'],
                                                             request.session['port_number']))
        username, password = request.session['credentials']
        connection.simple_bind_s(username, password)
        try:
            connection.modify_s(dn, mod_attrs)
        except (ldap.NOT_ALLOWED_ON_RDN, ldap.OBJECT_CLASS_VIOLATION):
            return HttpResponse(json.dumps({'success': False, 'message': not_allowed_msg}),
                                content_type="application/json", status=200)
        connection.unbind_s()
        return HttpResponse(json.dumps({'success': True}), content_type="application/json", status=200)

    @handle_ldap_errors
    @handle_credentials_errors
    def delete(self, request, *args, **kwargs):
        mod_attrs = [(ldap.MOD_DELETE, kwargs['attribute'], [])]
        return self._change_ldap_profile(request, kwargs['subscriber_id'], mod_attrs,
                                         "Attribute deletion is not allowed")


    @handle_ldap_errors
    @handle_credentials_errors
    def put(self, request, *args, **kwargs):
        params = QueryDict(request.body)
        mod_attrs = [(ldap.MOD_REPLACE, kwargs['attribute'], [params['attribute_val'].encode('utf-8').strip()])]
        return self._change_ldap_profile(request, kwargs['subscriber_id'], mod_attrs,
                                         "Attribute updating is not allowed")


class ProfileAttributeCreateView(View):
    @handle_ldap_errors
    @handle_credentials_errors
    def post(self, request, *args, **kwargs):
        dn = request.POST['dn']
        attribute_key = request.POST['attribute_key']
        attribute_value = request.POST['attribute_val'].encode('utf-8').strip()
        connection = ldap.initialize('ldap://{0}:{1}'.format(request.session['host_address'],
                                                             request.session['port_number']))
        username, password = request.session['credentials']
        connection.simple_bind_s(username, password)
        mod_attrs = [(ldap.MOD_ADD, attribute_key, attribute_value)]
        try:
            connection.modify_s(dn, mod_attrs)
        except (ldap.NOT_ALLOWED_ON_RDN, ldap.OBJECT_CLASS_VIOLATION):
            return HttpResponse(json.dumps({'success': False, 'message': "Attribute adding is not allowed"}),
                                content_type="application/json", status=200)
        connection.unbind_s()
        return HttpResponse(json.dumps({'success': True}), content_type="application/json", status=200)

