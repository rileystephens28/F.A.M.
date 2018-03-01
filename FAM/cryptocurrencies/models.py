from django.db import models
from sources.models import CryptoExchange

class Cryptocurrency(models.Model):
    base = models.CharField(max_length=10)
    quote = models.CharField(max_length=10)
    exchange = models.ForeignKey(CryptoExchange, on_delete=models.CASCADE,)
    bid = models.FloatField(default = None, null = True)
    ask = models.FloatField(default = None, null = True)
    last = models.FloatField(default = None, null = True)
    base_volume = models.FloatField(default = None, null = True)
    quote_volume = models.FloatField(default = None, null = True)
    last_updated = models.DateTimeField(default = None, null = True)

    #def get_currency(self,base,quote,exchange):
#        if Cryptocurrency.objects.filter(base=base,quote=quote,exchange_id=CryptoExchange.objects.get(name=exchange)):
#            return Cryptocurrency.objects.get(base=base,quote=quote,exchange_id=CryptoExchange.objects.get(name=exchange))
#        else:
#            return "That currency pair does not exist on %s" % exchange
