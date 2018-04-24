from django.db import models
from sources.models import StockExchange, OptionExchange, CryptoExchange
import requests
import json
from datetime import datetime, timedelta
from assets.update_data.tradier import Tradier
from assets.update_data.hitbtc import HitBTC

global tradier, hitbtc
tradier = Tradier()
hitbtc = HitBTC()

class Stock(models.Model):
    symbol = models.CharField(max_length=50)
    exchange = models.ForeignKey(StockExchange, on_delete=models.CASCADE,unique=False)
    bid = models.FloatField(default = None)
    ask = models.FloatField(default = None)
    last = models.FloatField(default = None)
    volume = models.FloatField(default = None, null = True)
    high =  models.FloatField(default = None, null = True)
    low =  models.FloatField(default = None, null = True)
    open_price =  models.FloatField(default = None, null = True)
    close_price =  models.FloatField(default = None, null = True)
    week_chart = models.TextField(default = None, null = True)
    month_chart = models.TextField(default = None, null = True)

    def get_week_chart(self):
        return json.loads(self.week_chart)

    def update_week_chart(self):
        self.week_chart = tradier.get_candlestick(self.symbol,7)
        self.save()

    def get_month_chart(self):
        return json.loads(self.month_chart)

    def update_month_chart(self):
        self.week_chart = tradier.get_candlestick(self.symbol,30)
        self.save()

    def update_data(self):
        ticker = tradier.get_ticker(self.symbol)
        self.bid = ticker["bid"]
        self.ask = ticker["ask"]
        self.last = ticker["last"]
        self.volume = ticker["volume"]
        self.high = ticker["high"]
        self.low = ticker["low"]
        self.open_price = ticker["open"]
        self.close_price =  ticker["close"]
        self.save()

    def __str__(self):
        return self.symbol


class Option(models.Model):
    underlying = models.ForeignKey(Stock, on_delete=models.CASCADE,)
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
    high =  models.FloatField(default = None, null = True)
    low =  models.FloatField(default = None, null = True)
    open_price =  models.FloatField(default = None, null = True)
    close_price =  models.FloatField(default = None, null = True)
    week_chart = models.TextField(default = None, null = True)
    month_chart = models.TextField(default = None, null = True)

    def get_week_chart(self):
        return json.loads(self.week_chart)

    def update_week_chart(self):
        self.week_chart = tradier.get_candlestick(self.symbol,7)
        self.save()

    def get_month_chart(self):
        return json.loads(self.month_chart)

    def update_month_chart(self):
        self.week_chart = tradier.get_candlestick(self.symbol,30)
        self.save()

    def update_data(self):
        ticker = tradier.get_ticker(self.symbol)
        self.bid = ticker["bid"]
        self.ask = ticker["ask"]
        self.last = ticker["last"]
        self.volume = ticker["volume"]
        self.open_interest = ticker["open_interest"]
        self.high = ticker["high"]
        self.low = ticker["low"]
        self.open_price = ticker["open"]
        self.close_price =  ticker["close"]
        self.save()

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
    high =  models.FloatField(default = None, null = True)
    low =  models.FloatField(default = None, null = True)
    base_volume = models.FloatField(default = None, null = True)
    quote_volume = models.FloatField(default = None, null = True)
    week_chart = models.TextField(default = None, null = True)
    month_chart = models.TextField(default = None, null = True)

    def get_week_chart(self):
        return json.loads(self.week_chart)

    def update_week_chart(self):
        self.week_chart = hitbtc.get_candlestick(self.symbol,7)
        self.save()

    def get_month_chart(self):
        return json.loads(self.month_chart)

    def update_month_chart(self):
        self.week_chart = hitbtc.get_candlestick(self.symbol,30)
        self.save()

    def update_ticker(self):
        ticker = hitbtc.get_ticker(self.symbol)
        self.bid = float(ticker_data["bid"])
        self.ask = float(ticker_data["ask"])
        self.last = float(ticker_data["last"])
        self.high = float(ticker_data["high"])
        self.low = float(ticker_data["low"])
        self.base_volume = float(ticker_data["volume"])
        self.quote_volume = float(ticker_data["volumeQuote"])
        self.save()

    def __str__(self):
        return self.symbol
