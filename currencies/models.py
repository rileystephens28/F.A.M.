from json import loads
from datetime import datetime, timedelta
from django.db import models
from exchanges.models import Exchange

class Currency(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)    # what exchange calls coin
    name = models.CharField(max_length=10)      # what we will can coin (EX: USDT is named USD)

class CurrencyPair(models.Model):

    base = models.ForeignKey(Currency, on_delete=models.CASCADE,related_name="base")
    quote = models.ForeignKey(Currency, on_delete=models.CASCADE,related_name="quote")

    bid = models.FloatField(default=None, null=True)
    ask = models.FloatField(default=None, null=True)
    last = models.FloatField(default=None, null=True)

    base_volume = models.FloatField(default=None, null=True)
    quote_volume = models.FloatField(default=None, null=True)

    day_chart = models.TextField(default = None, null = True)
    week_chart = models.TextField(default = None, null = True)
    month_chart = models.TextField(default = None, null = True)
    year_chart = models.TextField(default = None, null = True)

    def get_day_chart(self):
        return loads(self.day_chart)

    def get_week_chart(self):
        return loads(self.week_chart)

    def get_month_chart(self):
        return loads(self.month_chart)

    def get_year_chart(self):
        return loads(self.year_chart)

    def get_quote_value(self,quote_currency):  # implement by looking at last price of quote_currency (USD) and calulating holdings
        pass

    def __str__(self):
        return self.symbol
