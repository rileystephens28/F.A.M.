from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from accounts.models import Account
from django.contrib.auth.models import User

class AddInvestment(forms.Form):
    purchase_date = forms.DateField(required=False)
    purchase_price = forms.FloatField(required=True)
    quantity = forms.FloatField(required=True)

    def __init__(self, *args, **kwargs):
        super(AddInvestment, self).__init__(*args, **kwargs)
        self.fields['purchase_date'].widget.attrs['placeholder'] = "Ex: 2017-02-17"
        self.fields['purchase_price'].widget.attrs['placeholder'] = "Ex: 150"
        self.fields['quantity'].widget.attrs['placeholder'] = "Ex: 2"



class SignupForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'First Name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder':'Last Name'}))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = "Username"
        self.fields['password1'].widget.attrs['placeholder'] = "Password"
        self.fields['password2'].widget.attrs['placeholder'] = "Reenter Password"

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'password1', 'password2', )

class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = "Username"
        self.fields['password'].widget.attrs['placeholder'] = "Password"
