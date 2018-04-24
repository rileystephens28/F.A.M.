from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Account
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='First Name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last Name')

class AddInvestment(forms.Form):
    purchase_date = forms.DateField(required=False, help_text='Purchase Date')
    purchase_price = forms.FloatField(required=True, help_text='Purchase Price')
    quantity = forms.FloatField(required=True, help_text='Quantity')
