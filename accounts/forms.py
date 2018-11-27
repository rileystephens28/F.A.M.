from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile
from exchanges.models import Exchange

class SignupForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = "First Name"
        self.fields['last_name'].widget.attrs['placeholder'] = "Last Name"
        self.fields['email'].widget.attrs['placeholder'] = "Email"
        self.fields['password1'].widget.attrs['placeholder'] = "Password"
        self.fields['password2'].widget.attrs['placeholder'] = "Reenter Password"

    class Meta:
        model = User
        fields = ('first_name', 'last_name','email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    username = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = "Email"
        self.fields['password'].widget.attrs['placeholder'] = "Password"

    class Meta:
        model = User
        fields = ( 'email', 'password')

class ApiKeyForm(forms.Form):

    exchange= forms.ModelChoiceField(queryset = Exchange.objects.filter().order_by("name"), required=True)
    api_key = forms.CharField(required=True)
    secret_key = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super(ApiKeyForm, self).__init__(*args, **kwargs)
        self.fields['api_key'].widget.attrs.update({'placeholder':"API Key",'class' : 'form-control col-md-7 col-xs-12'})
        self.fields['secret_key'].widget.attrs.update({'placeholder':"Secret Key",'class' : 'form-control col-md-7 col-xs-12'})
