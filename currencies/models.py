from json import loads
from datetime import datetime, timedelta
from django.db import models
from exchanges.models import Exchange

class Currency(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)    # what exchange calls coin
    name = models.CharField(max_length=10)      # what we will can coin (EX: USDT is named USD)

    def __str__(self):
        return self.symbol

class CurrencyPair(models.Model):

    base = models.ForeignKey(Currency, on_delete=models.CASCADE,related_name="base")
    quote = models.ForeignKey(Currency, on_delete=models.CASCADE,related_name="quote")
    symbol = models.CharField(max_length=30, default="")

    bid = models.FloatField(default=0)
    ask = models.FloatField(default=0)
    last = models.FloatField(default=0)

    base_volume = models.FloatField(default=0)
    quote_volume = models.FloatField(default=0)

    def get_quote_value(self,quote_currency):  # implement by looking at last price of quote_currency (USD) and calulating holdings
        pass

    def __str__(self):
        return self.base.symbol+" "+self.quote.symbol
