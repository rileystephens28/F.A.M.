from django.db import models
from sources.models import StockExchange, OptionExchange, CryptoExchange
import requests
import json

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

    def update_data(self):
        TRADIER_API_KEY = 'XCp8C02gIfnzIW99aTTU4jnPQGVJ'
        s = requests.Session()
        s.headers.update({'Authorization':'Bearer ' + TRADIER_API_KEY, 'Accept':'application/json'})
        url = 'https://api.tradier.com/v1/markets/quotes'
        params = {"symbols":self.symbol}
        r = s.get(url, params=params)
        content = json.loads(r.text)
        quote = content["quotes"]["quote"]
        self.bid = quote["bid"]
        self.ask = quote["ask"]
        self.last = quote["last"]
        self.volume = quote["volume"]
        self.high = quote["high"]
        self.low = quote["low"]
        self.open_price = quote["open"]
        self.close_price =  quote["close"]
        self.save()


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


class Cryptocurrency(models.Model):
    base = models.CharField(max_length=10)
    quote = models.CharField(max_length=10)
    symbol = models.CharField(max_length=20)
    exchange = models.ForeignKey(CryptoExchange, on_delete=models.CASCADE,)
    bid = models.FloatField(default = None, null = True)
    ask = models.FloatField(default = None, null = True)
    last = models.FloatField(default = None, null = True)
    base_volume = models.FloatField(default = None, null = True)
    quote_volume = models.FloatField(default = None, null = True)
    last_updated = models.DateTimeField(default = None, null = True)

    def __str__(self):
        return self.symbol

    def update_data(self):
        ticker_data = requests.get('https://api.hitbtc.com/api/2/public/ticker/' + self.symbol.upper()).json()
        self.bid = float(ticker_data["bid"])
        self.ask = float(ticker_data["ask"])
        self.last = float(ticker_data["last"])
        self.base_volume = float(ticker_data["volume"])
        self.quote_volume = float(ticker_data["volumeQuote"])
        self.save()
