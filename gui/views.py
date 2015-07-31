from django.views.generic.base import TemplateView
from django.views.generic import View
from django.http import HttpResponse
from forms import LoginForm
from helpers import SessionInfo
import json
import ldap


class HomePageView(TemplateView):

    template_name = "show.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        return context


class LoginView(View):
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if not form.is_valid():
            return HttpResponse(json.dumps({'success': False, 'validation_error': True, 'message': form.errors}), content_type="application/json", status=200)
        try:
            connection = ldap.initialize('ldap://127.0.0.1:389')
            connection.simple_bind_s(form.cleaned_data['username'], form.cleaned_data['password'])
            request.session['credentials'] = form.cleaned_data['username'], form.cleaned_data['password']
            connection.unbind_s()

        except ldap.SERVER_DOWN:
            return HttpResponse(json.dumps({'success': False, 'message': "Can't contact ldap server"}), content_type="application/json", status=200)

        except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
            return HttpResponse(json.dumps({'success': False, 'message': "Invalid Credentials"}), content_type="application/json", status=200)

        return HttpResponse(json.dumps({'success': True}), content_type='application/json', status=200)
