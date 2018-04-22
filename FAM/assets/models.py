from django.db import models
from sources.models import StockExchange, OptionExchange, CryptoExchange
import requests
import json
from datetime import datetime, timedelta

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
    week_chart = models.TextField(default = None, null = True)
    month_chart = models.TextField(default = None, null = True)

    def get_week_chart(self):
        return json.loads(self.week_chart)

    def update_week_chart(self):
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        week_ago = week_ago.strftime("%Y-%m-%d %H-%M")
        TRADIER_API_KEY = 'XCp8C02gIfnzIW99aTTU4jnPQGVJ'
        s = requests.Session()
        s.headers.update({'Authorization':'Bearer ' + TRADIER_API_KEY, 'Accept':'application/json'})
        url = 'https://api.tradier.com/v1/markets/timesales?symbol=AAPL'
        params = {"symbol":self.symbol,'interval':'15min','start':week_ago}
        r = s.get(url, params=params)
        raw_data = json.loads(r.text)
        cleaned_data = []
        x = 0
        for data in raw_data["series"]['data']:
            if x > 2:
                cleaned_data.append(data)
                x = 0
            else:
                x += 1
        text_data = json.dumps(cleaned_data)
        self.week_chart = text_data

    def get_month_chart(self):
        return json.loads(self.month_chart)

    def update_month_chart(self):
        today = datetime.now()
        week_ago = today - timedelta(days=30)
        week_ago = week_ago.strftime("%Y-%m-%d %H-%M")
        TRADIER_API_KEY = 'XCp8C02gIfnzIW99aTTU4jnPQGVJ'
        s = requests.Session()
        s.headers.update({'Authorization':'Bearer ' + TRADIER_API_KEY, 'Accept':'application/json'})
        url = 'https://api.tradier.com/v1/markets/timesales?symbol=AAPL'
        params = {"symbol":self.symbol,'interval':'15min','start':week_ago}
        r = s.get(url, params=params)
        raw_data = json.loads(r.text)
        cleaned_data = []
        x = 0
        for data in raw_data["series"]['data']:
            if x > 45:
                cleaned_data.append(data)
                x = 0
            else:
                x += 1
        text_data = json.dumps(cleaned_data)
        self.month_chart = text_data

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

    def __str__(self):
        return self.symbol


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
    week_chart = models.TextField(default = None, null = True)
    month_chart = models.TextField(default = None, null = True)

    def get_week_chart(self):
        return json.loads(self.week_chart)

    def get_month_chart(self):
        return json.loads(self.month_chart)

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
    week_chart = models.TextField(default = None, null = True)
    month_chart = models.TextField(default = None, null = True)

    def get_week_chart(self):
        return json.loads(self.week_chart)

    def get_month_chart(self):
        return json.loads(self.month_chart)

    def update_ticker(self):
        ticker_data = requests.get('https://api.hitbtc.com/api/2/public/ticker/' + self.symbol.upper()).json()
        self.bid = float(ticker_data["bid"])
        self.ask = float(ticker_data["ask"])
        self.last = float(ticker_data["last"])
        self.base_volume = float(ticker_data["volume"])
        self.quote_volume = float(ticker_data["volumeQuote"])
        self.save()


    def __str__(self):
        return self.symbol
