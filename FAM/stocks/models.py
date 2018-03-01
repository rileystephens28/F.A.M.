from django.db import models
from sources.models import StockExchange

class Stock(models.Model):
    company = models.CharField(max_length=500, null = True)
    symbol = models.CharField(max_length=50)
    exchange = models.ForeignKey(StockExchange, on_delete=models.CASCADE,unique=False)
    price = models.FloatField(default = None)
    bid = models.FloatField(default = None)
    ask = models.FloatField(default = None)
    last = models.FloatField(default = None)
    volume = models.FloatField(default = None, null = True)
    high =  models.FloatField(default = None, null = True)
    low =  models.FloatField(default = None, null = True)
    open_price =  models.FloatField(default = None, null = True)
    close_price =  models.FloatField(default = None, null = True)

    def __str__(self):
        return self.symbol
