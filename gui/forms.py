from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
    host_address = forms.CharField(max_length=100)
    port_number = forms.IntegerField()

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        cleaned_data['username'] = str(cleaned_data['username'])
        cleaned_data['password'] = str(cleaned_data['password'])
        cleaned_data['host_address'] = str(cleaned_data['host_address'])
        cleaned_data['port_number'] = str(cleaned_data['port_number'])


class SubscriberForm(forms.Form):
    subscriber_id = forms.CharField(max_length=100)