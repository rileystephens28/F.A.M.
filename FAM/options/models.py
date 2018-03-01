from django.db import models
from sources.models import OptionExchange

class Option(models.Model):
    underlying = models.CharField(max_length=10,default = None)
    exchange = models.ForeignKey(OptionExchange, on_delete=models.CASCADE,)
    symbol = models.CharField(max_length=50)
    expiration = models.DateField()
    type = models.CharField(max_length=4) #call or put
    strike = models.FloatField()
    bid = models.FloatField()
    ask = models.FloatField()
    last = models.FloatField(default = None)
    volume = models.FloatField(default = None)
    open_interest = models.FloatField(default = None)

    def __str__(self):
        return self.symbol
