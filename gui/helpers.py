from django.http import HttpResponse
import ldap
import json


def handle_ldap_errors(func):
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except ldap.SERVER_DOWN:
            return HttpResponse(json.dumps({'success': False, 'message': "Can't contact ldap server"}), content_type="application/json", status=200)

        except (ldap.INVALID_CREDENTIALS, ldap.NO_SUCH_OBJECT):
            return HttpResponse(json.dumps({'success': False, 'message': "Invalid Credentials"}), content_type="application/json", status=200)

    return wrapper