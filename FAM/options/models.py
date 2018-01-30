from django.db import models

class Option(models.Model):
    symbol = models.CharField(max_length=10)
    expiration = models.DateField()
    type = models.CharField(max_length=4) #call or put
    strike = models.FloatField()
    bid = models.FloatField()
    ask = models.FloatField()
    last = models.FloatField(default = None)
    volume = models.FloatField(default = None)
    open_interest = models.FloatField(default = None)
