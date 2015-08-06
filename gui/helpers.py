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


def handle_credentials_errors(func):
    def wrapper(view_object, *args, **kwargs):
        if 'sessionid' not in view_object.request.COOKIES:
            return HttpResponse(json.dumps({'success': False, 'message': "You need to authenticate",
                                            'auth_error': True}), content_type="application/json", status=200)
        return func(view_object, *args, **kwargs)

    return wrapper


class LdapHandler(object):
    def _connect(self, host_address, port_number, username, password):
        """abstracts the connection from the initiation in order to facilitate the mocking during the unit tests"""
        connection = ldap.initialize('ldap://{0}:{1}'.format(host_address, port_number))
        connection.simple_bind_s(username, password)
        return connection

    def __init__(self, host_address, port_number, username, password):
        self.connection = self._connect(host_address, port_number, username, password)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.unbind_s()

    def search(self, subscriber_id):
        ldap_profiles = self.connection.search_s('o=TE Data,c=EG', ldap.SCOPE_SUBTREE,
                                            '(uid=%s)' % subscriber_id)

        return {profile[0]: profile[1] for profile in ldap_profiles}

    def change_profile(self, subscriber_id, subtree, attributes):
        dn = "uid={0},{1}".format(subscriber_id, subtree)
        self.connection.modify_s(dn, attributes)

    def add_attribute(self, dn, attributes):
        self.connection.modify_s(dn, attributes)

