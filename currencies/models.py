from json import loads
from datetime import datetime, timedelta
from django.db import models
from exchanges.models import Exchange

class Currency(models.Model):
    """ Indiviual cryptocurrency DB model """

    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)    # what exchange calls coin
    name = models.CharField(max_length=10)      # what we will can coin (EX: USDT is named USD)

    def get_usd_value(self):
        """ Returns USD price of cryptocurrency that calls this method """

        if self.name != "USD":
            if CurrencyPair.objects.filter(symbol=self.symbol+"USDT",base__exchange=self.exchange).exists():
                pair = CurrencyPair.objects.get(symbol=self.symbol+"USDT",base__exchange=self.exchange)
                price = pair.last
            elif CurrencyPair.objects.filter(symbol=self.symbol+"USDC",base__exchange=self.exchange).exists():
                pair = CurrencyPair.objects.get(symbol=self.symbol+"USDC",base__exchange=self.exchange)
                price = pair.last
            elif CurrencyPair.objects.filter(symbol=self.symbol+"USD",base__exchange=self.exchange).exists():
                pair = CurrencyPair.objects.get(symbol=self.symbol+"USD",base__exchange=self.exchange)
                price = pair.last
            elif CurrencyPair.objects.filter(symbol=self.symbol+"BTC",base__exchange=self.exchange).exists():
                btc_pair = CurrencyPair.objects.get(symbol=self.symbol+"BTC",base__exchange=self.exchange)
                if CurrencyPair.objects.filter(symbol="BTCUSDT",base__exchange=self.exchange).exists():
                    btc_usd = CurrencyPair.objects.get(symbol="BTCUSDT",base__exchange=self.exchange)
                elif CurrencyPair.objects.filter(symbol="BTCUSDC",base__exchange=self.exchange).exists():
                    btc_usd = CurrencyPair.objects.get(symbol="BTCUSDC",base__exchange=self.exchange)
                elif CurrencyPair.objects.filter(symbol="BTCUSD",base__exchange=self.exchange).exists():
                    btc_usd = CurrencyPair.objects.get(symbol="BTCUSD",base__exchange=self.exchange)
                price = btc_pair.last*btc_usd.last
            else:
                price = 0
        else:
            price = 1

        return price

    def __str__(self):
        return self.symbol

class CurrencyPair(models.Model):
    """ DB model that represents a currency pair and stores market data"""

    base = models.ForeignKey(Currency, on_delete=models.CASCADE,related_name="base")
    quote = models.ForeignKey(Currency, on_delete=models.CASCADE,related_name="quote")
    symbol = models.CharField(max_length=30, default="")

    bid = models.FloatField(default=0)
    ask = models.FloatField(default=0)
    last = models.FloatField(default=0)

    base_volume = models.FloatField(default=0)
    quote_volume = models.FloatField(default=0)

    def __str__(self):
        return self.base.symbol+" "+self.quote.symbol
