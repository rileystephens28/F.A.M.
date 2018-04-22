from django.db import models
from django.contrib.auth.models import User
from assets.models import Stock, Option, Cryptocurrency
import django
import datetime

class StockInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Stock, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    date = models.DateField(default = django.utils.timezone.now)
    #chart = models.TextField(default = None, null = True)

class OptionInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Option, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    date = models.DateField(default = django.utils.timezone.now)
    #chart = models.TextField(default = None, null = True)

class CryptoInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    date = models.DateField(default = django.utils.timezone.now)
    #chart = models.TextField(default = None, null = True)
