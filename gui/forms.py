from django import forms


def _encode_utf8(string):
    return string.encode('utf-8').strip()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
    host_address = forms.CharField(max_length=100)
    port_number = forms.IntegerField()
    scope_subtree = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        if 'username' in cleaned_data:
            cleaned_data['username'] = _encode_utf8(cleaned_data['username'])
        if 'password' in cleaned_data:
            cleaned_data['password'] = _encode_utf8(cleaned_data['password'])
        if 'host_address' in cleaned_data:
            cleaned_data['host_address'] = _encode_utf8(cleaned_data['host_address'])
        if 'scope_subtree' in cleaned_data:
            cleaned_data['scope_subtree'] = _encode_utf8(cleaned_data['scope_subtree'])


class SubscriberForm(forms.Form):
    subscriber_id = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(SubscriberForm, self).clean()
        cleaned_data['subscriber_id'] = _encode_utf8(cleaned_data['subscriber_id'])


class AttributeUpdateForm(forms.Form):
    attribute_val = forms.CharField(max_length=100)


class AttributeCreateForm(forms.Form):
    attribute_key = forms.CharField(max_length=100)
    attribute_val = forms.CharField(max_length=100)
    dn = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(AttributeCreateForm, self).clean()
        cleaned_data['attribute_key'] = _encode_utf8(cleaned_data['attribute_key'])
        cleaned_data['attribute_val'] = _encode_utf8(cleaned_data['attribute_val'])
        cleaned_data['dn'] = _encode_utf8(cleaned_data['dn'])