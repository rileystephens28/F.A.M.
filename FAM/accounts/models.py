from django.db import models
from django.contrib.auth.models import User
from assets.models import Stock, Option, Cryptocurrency

class StockInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Stock, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)

class OptionInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Option, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)

class CryptoInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
