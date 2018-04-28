from django.db import models
from django.contrib.auth.models import User
from assets.models import Stock, Option, Cryptocurrency
import django
import datetime
import json
from assets.update_data.hitbtc import HitBTC
from assets.update_data.tradier import Tradier

global hitbtc, tradier
hitbtc = HitBTC()
tradier = Tradier()

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    amount_invested = models.FloatField(blank = True, default=0)
    current_balance = models.FloatField(blank = True, default=0)
    chart = models.TextField(default = None, null = True)

    def add_investment(self, symbol, price, quantity, purchase_date):
        if Stock.objects.filter(symbol=symbol):
            new_investment = StockInvestment()
            new_investment.asset = Stock.objects.get(symbol=symbol)
            self.amount_invested += float('%.2f' %(price * quantity))
            self.current_balance += float('%.2f' %(price * quantity))
        elif Option.objects.filter(symbol=symbol):
            new_investment = OptionInvestment()
            new_investment.asset = Option.objects.get(symbol=symbol)
            self.amount_invested += float('%.2f' %(price * quantity))
            self.current_balance += float('%.2f' %(price * quantity))
        elif Cryptocurrency.objects.filter(symbol=symbol):
            new_investment = CryptoInvestment()
            new_investment.asset = Cryptocurrency.objects.get(symbol=symbol)
            add_amount = float('%.2f' %(new_investment.asset.get_usd_value() * quantity))
            self.amount_invested += add_amount
            self.current_balance += add_amount

        new_investment.investor = self.user
        new_investment.date = purchase_date
        new_investment.purchase_price = price
        new_investment.quantity = quantity
        new_investment.save()
        self.save()

    def get_investment(self,symbol):

        if Stock.objects.filter(symbol=symbol):
            asset = Stock.objects.get(symbol=symbol)
            if StockInvestment.objects.filter(investor=self.user, asset=asset):
                return StockInvestment.objects.get(investor=self.user, asset=asset)
        elif Option.objects.filter(symbol=symbol):
            asset = Option.objects.get(symbol=symbol)
            if OptionInvestment.objects.filter(investor=self.user, asset=asset):
                return OptionInvestment.objects.get(investor=self.user, asset=asset)
        elif Cryptocurrency.objects.filter(symbol=symbol):
            asset = Cryptocurrency.objects.get(symbol=symbol)
            if CryptoInvestment.objects.filter(investor=self.user, asset=asset):
                return CryptoInvestment.objects.get(investor=self.user, asset=asset)

    def get_all_investments(self):
        investments = []

        for investment in StockInvestment.objects.filter(investor=self.user):
            investments.append(investment)
        for investment in OptionInvestment.objects.filter(investor=self.user):
            investments.append(investment)
        for investment in CryptoInvestment.objects.filter(investor=self.user):
            investments.append(investment)
        all_investments = {}
        for investment in investments:
            if not investment.asset.symbol in investments:
                all_investments[investment.asset.symbol] = [investment]
            else:
                all_investments[investment.asset.symbol].append(investment)
        return all_investments

    def update_current_balance(self):
        balance = 0
        investments = self.get_all_investments()
        for key, value in investments.items():
            for item in value:
                if Stock.objects.filter(symbol=item.asset.symbol) or Option.objects.filter(symbol=item.asset.symbol):
                    balance += item.asset.last * item.quantity
                else:
                    balance += item.asset.get_usd_value() * item.quantity

        if balance != self.current_balance:
            self.current_balance = balance
            self.current_balance = '%.2f' %self.current_balance
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
            asset.update_chart()
            asset_chart = asset.get_chart()
            asset_dates = list([str(datetime.datetime.strptime(item['time'],"%Y-%m-%dT%H:%M:%S").date()) for item in asset_chart])
            for date in asset_dates:
                price_list = list([float(item["close"]) for item in asset_chart if str(datetime.datetime.strptime(item['time'],"%Y-%m-%dT%H:%M:%S").date()) == date])
                if not date in chart.keys():
                    chart[date] = list([item for item in price_list])
                else:
                    chart[date] += price_list

        for date in chart.keys():
            if len(chart[date]) > 1:
                chart[date] = sum(chart[date])/len(chart[date])
        chart = json.dumps(chart)

        self.chart = chart
        self.save()

class StockInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Stock, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    quantity = models.FloatField(default = None, null = True)
    date = models.DateField(default = None)
    performance = models.FloatField(default = None, null = True)
    chart = models.TextField(default = None, null = True)

    def get_chart(self):
        return json.loads(self.chart)

    def update_chart(self):
        days = (datetime.datetime.now().date() - self.date).days
        self.chart = tradier.get_candlestick(self.asset.symbol,days)
        self.save()

    def update_performance(self):
        self.performance = ((self.asset.bid + self.asset.ask)/2 * self.quantity) - (self.purchase_price * self.quantity)
        self.save()


class OptionInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Option, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    quantity = models.FloatField(default = None, null = True)
    date = models.DateField(default = None)
    performance = models.FloatField(default = None, null = True)
    chart = models.TextField(default = None, null = True)

    def get_chart(self):
        return json.loads(self.chart)

    def update_chart(self):
        days = (datetime.datetime.now().date() - self.date).days
        self.chart = tradier.get_candlestick(self.asset.symbol,days)
        self.save()

    def update_performance(self):
        self.performance = ((self.asset.bid + self.asset.ask)/2 * self.quantity) - (self.purchase_price * self.quantity)
        self.save()

class CryptoInvestment(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Cryptocurrency, on_delete=models.CASCADE)
    purchase_price = models.FloatField(default = None)
    quantity = models.FloatField(default = None, null = True)
    date = models.DateField(default = None)
    performance = models.FloatField(default = None, null = True)
    chart = models.TextField(default = None, null = True)

    def get_chart(self):
        return json.loads(self.chart)

    def update_chart(self):
        days = (datetime.datetime.now().date() - self.date).days
        self.chart = hitbtc.get_candlestick(self.asset.symbol,days)
        self.save()

    def update_performance(self):
        self.performance = ((self.asset.bid + self.asset.ask)/2 * self.quantity) - (self.purchase_price * self.quantity)
        self.save()
