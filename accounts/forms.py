from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = "Email"
        self.fields['password1'].widget.attrs['placeholder'] = "Password"
        self.fields['password2'].widget.attrs['placeholder'] = "Reenter Password"

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    email = forms.EmailField(required=True)


    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = "Email"
        self.fields['password'].widget.attrs['placeholder'] = "Password"

    class Meta:
        model = User
        fields = ('email', 'password')

class NameForm(AuthenticationForm): # Inherit from the right form

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = "First Name"
        self.fields['last_name'].widget.attrs['placeholder'] = "Last Name"

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name' )
