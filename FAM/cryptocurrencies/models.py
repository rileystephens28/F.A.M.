from django.db import models
from sources import Source

class Cryptocurrency(models.Model):
    base = models.CharField(max_length=10)
    quote = models.CharField(max_length=10)
    exchange = models.ForeignKey(Source)
    bid = models.FloatField(default = None)
    ask = models.FloatField(default = None)
    last = models.FloatField(default = None)
    base_volume = models.FloatField(default = None)
    quote_volume = models.FloatField(default = None)
