from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        cleaned_data['username'] = str(cleaned_data['username'])
        cleaned_data['password'] = str(cleaned_data['password'])