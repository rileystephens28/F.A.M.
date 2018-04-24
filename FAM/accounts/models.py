from django.db import models
from django.contrib.auth.models import User
from assets.models import Stock, Option, Cryptocurrency
import django
import datetime
from assets.update_data.hitbtc import HitBTC
from assets.update_data.tradier import Tradier

global hitbtc, tradier
hitbtc = HitBTC()
tradier = Tradier()

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    name = models.CharField(blank=True, max_length=255)
    amount_invested = models.FloatField(blank = True, default=0)
    current_balance = models.FloatField(blank = True, default=0)
    chart = models.TextField(default = None, null = True)

    def add_investment(self, symbol, price, quantity):
        if Stock.objects.filter(symbol=symbol):
            new_investment = StockInvestment()
            new_investment.asset = Stock.objects.get(symbol=symbol)
            self.amount_invested += new_investment.purchase_price * new_investment.quantity
            self.current_balance += new_investment.purchase_price * new_investment.quantity
        elif Option.objects.filter(symbol=symbol):
            new_investment = OptionInvestment()
            new_investment.asset = Option.objects.get(symbol=symbol)
            self.amount_invested += new_investment.purchase_price * new_investment.quantity
            self.current_balance += new_investment.purchase_price * new_investment.quantity
        elif Cryptocurrency.objects.filter(symbol=symbol):
            new_investment = CryptoInvestment()
            new_investment.asset = Cryptocurrency.objects.get(symbol=symbol)
            usd_amount = hitbtc.get_ticker(symbol = asset.base + "USDT")
            self.amount_invested += usd_amount * new_investment.quantity
            self.current_balance += usd_amount * new_investment.quantity
        new_investment.investor = self.user
        new_investment.purchase_price = price
        new_investment.quantity = quantity
        new_investment.save()
        self.save()

    def get_investment(self,symbol):
        assets = []
        if StockInvestment.objects.filter(investor=self.user, symbol=symbol):
            for asset in StockInvestment.objects.filter(investor=self.user, symbol = symbol):
                assets.append(asset)
        if OptionInvestment.objects.filter(investor=self.user, symbol=symbol):
            for asset in OptionInvestment.objects.filter(investor=self.user, symbol = symbol):
                assets.append(asset)
        if CryptoInvestment.objects.filter(investor=self.user, symbol=symbol):
            for asset in CryptoInvestment.objects.filter(investor=self.user, symbol = symbol):
                assets.append(asset)
        return {symbol:assets}

    def get_all_investments(self):
        assets = []
        for asset in StockInvestment.objects.filter(investor=self.user):
            assets.append(asset)
        for asset in OptionInvestment.objects.filter(investor=self.user):
            assets.append(asset)
        for asset in CryptoInvestment.objects.filter(investor=self.user):
            assets.append(asset)
        investments = {}
        for asset in assets:
            if not investments.has_key(asset.symbol):
                investments[asset.symbol] = [asset]
            else:
                investments[asset.symbol].append(asset)
        return investments

    def update_current_balance(self):
        balance = 0
        investments = self.get_all_investments()
        for key, value in investments.items():
            for item in value:
                item.update_data()
                balance += item.price * item.quantity

        if balance != self.current_balance:
            self.current_balance = balance
            self.save()

    def get_chart(self):
        return json.loads(self.chart)

    def update_chart(self):
        assets = []
        for asset in StockInvestment.objects.filter(investor=self.user):
            assets.append(asset)
        for asset in OptionInvestment.objects.filter(investor=self.user):
            assets.append(asset)
        for asset in CryptoInvestment.objects.filter(investor=self.user):
            assets.append(asset)

        chart = {}
        for asset in assets:
            asset_chart = asset.get_chart()
            asset_dates = list([item[time] for item in asset_chart])
            for date in asset_dates:
                if not charts.has_key(date):
                    day_list = list([item["close"] for item in asset_chart if item["time"] == date])
                    chart[date] = [(sum(day_list)/len(day_list)) * asset.quantity]
                else:
                    day_list = list([item["close"] for item in asset_chart if item["time"] == date])
                    chart[date].append((sum(day_list)/len(day_list)) * asset.quantity)

        for key,val in chart.items():
            chart[key] = sum(val)

        for key,val in chart.items():
            print (key, val)

class StockInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Stock, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    quantity = models.FloatField(default = None, null = True)
    date = models.DateField(default = django.utils.timezone.now)
    performance = models.FloatField(default = None, null = True)
    chart = models.TextField(default = None, null = True)

    def get_chart(self):
        return json.loads(self.chart)

    def update_chart(self):
        days = (datetime.now() - self.date).days
        self.chart = tradier.get_candlestick(self.symbol,days)
        self.save()

    def update_performance(self):
        self.performance = ((self.asset.bid + self.asset.ask)/2 * self.quantity) - (self.purchase_price * self.quantity)
        self.save()


class OptionInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Option, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    quantity = models.FloatField(default = None, null = True)
    date = models.DateField(default = django.utils.timezone.now)
    performance = models.FloatField(default = None, null = True)
    chart = models.TextField(default = None, null = True)

    def get_chart(self):
        return json.loads(self.chart)

    def update_chart(self):
        days = (datetime.now() - self.date).days
        self.chart = tradier.get_candlestick(self.symbol,days)
        self.save()

    def update_performance(self):
        self.performance = ((self.asset.bid + self.asset.ask)/2 * self.quantity) - (self.purchase_price * self.quantity)
        self.save()

class CryptoInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    quantity = models.FloatField(default = None, null = True)
    date = models.DateField(default = django.utils.timezone.now)
    performance = models.FloatField(default = None, null = True)
    chart = models.TextField(default = None, null = True)

    def get_chart(self):
        return json.loads(self.chart)

    def update_chart(self):
        days = (datetime.now() - self.date).days
        self.chart = tradier.get_candlestick(self.symbol,days)
        self.save()

    def update_performance(self):
        self.performance = ((self.asset.bid + self.asset.ask)/2 * self.quantity) - (self.purchase_price * self.quantity)
        self.save()
