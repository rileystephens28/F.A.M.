from django.db import models

class Stock(models.Model):
    symbol = models.CharField(max_length=10)
    bid = models.FloatField()
    ask = models.FloatField()
    last = models.FloatField(default = None)
    volume = models.FloatField(default = None)

    def __str__():
        return symbol
