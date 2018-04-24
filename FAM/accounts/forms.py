from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Account
from django.contrib.auth.models import User

class AddInvestment(forms.Form):
    purchase_date = forms.DateField(required=False)
    purchase_price = forms.FloatField(required=True)
    quantity = forms.FloatField(required=True)
