import time
from threading import Thread
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import datetime

from currencies.models import Currency, CurrencyPair
from exchanges.models import Exchange
from exchanges.apis.manager import ClientManager
from exchanges.apis.binance import BinanceClient
from exchanges.apis.poloniex import PoloniexClient


class UserManager(BaseUserManager):
    """A custom user manager to deal with emails as unique identifiers for auth
       instead of usernames. The default that's used is "UserManager" """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Creates and saves a User with the given email and password."""

        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        """ Creates base user without admin and staff privileges"""

        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """ Creates user with admin and staff privileges"""

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """ Custom user with email, password, first name, and last name fields"""
    username = None
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(null=True,blank=True,max_length=50)
    last_name = models.CharField(null=True,blank=True,max_length=50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    is_superuser = models.BooleanField('superuser status',default=False,help_text='Is the user allowed to have access to the admin')
    is_staff = models.BooleanField('staff status',default=False,help_text='Is the user allowed to have access to the admin')
    is_active = models.BooleanField('active',default=True,help_text= 'Is the user account currently active')
    objects = UserManager()

    def __str__(self):
        return self.first_name[0].upper() + self.first_name[1:] + " " + self.last_name[0].upper() + self.last_name[1:]

class Profile(models.Model):
    """ Extension of User model used to store api keys"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    binance_api_key = models.CharField(max_length=300,default="",blank=True)
    binance_secret_key = models.CharField(max_length=300,default="",blank=True)

    hitbtc_api_key = models.CharField(max_length=300,default="",blank=True)
    hitbtc_secret_key = models.CharField(max_length=300,default="",blank=True)

    poloniex_api_key = models.CharField(max_length=300,default="",blank=True)
    poloniex_secret_key = models.CharField(max_length=300,default="",blank=True)

    coinbase_api_key = models.CharField(max_length=300,default="",blank=True)
    coinbase_secret_key = models.CharField(max_length=300,default="",blank=True)

    def import_trades(self):
        """ Imports trades from all exchanges a user has linked """

        def get_trades_from_exchange():
            """ Sub methods used for threading that iterates through trades and saves them to DB"""

            exchange_obj = Exchange.objects.get(name=exchange[0].upper()+exchange[1:])
            currency_pairs = CurrencyPair.objects.filter(base__exchange=exchange_obj)
            for pair in currency_pairs:
                trades = manager.get_trade_history(exchange_obj.name.lower(),pair.base.symbol,pair.quote.symbol)
                print(pair.base.name,pair.quote.name)
                for trade in trades:
                    if not Trade.objects.filter(user=self.user,currency_pair=pair,time=trade['time'],type=trade['type']).exists():
                        new_trade = Trade()
                        new_trade.user = self.user
                        new_trade.currency_pair = pair
                        new_trade.quantity = trade['amount']
                        new_trade.price = trade['price']
                        new_trade.type = trade['type']
                        new_trade.time = trade['time']
                        new_trade.save()
                    time.sleep(.5)

        exchanges = {}
        if self.binance_api_key:
            exchanges['binance'] = {'api_key':self.binance_api_key, 'secret_key':self.binance_secret_key}
        if self.hitbtc_api_key:
            exchanges['hitbtc'] = {'api_key':self.hitbtc_api_key, 'secret_key':self.hitbtc_secret_key}
        if self.poloniex_api_key:
            exchanges['poloniex'] = {'api_key':self.poloniex_api_key, 'secret_key':self.poloniex_secret_key}

        manager = ClientManager(**exchanges)
        for exchange in exchanges.keys():
            get_trades_from_exchange()

    def total_balance(self):
        """ Retreives balances from all exchanges a user has linked """

        def assign_balance(_exchange):
            """ Sub methods used for threading that iterates through balances and saves them to DB"""

            balances = manager.get_balances(_exchange.name.lower())
            for balance in balances:
                if balance['tradable'] > 0:
                    try:
                        currency = Currency.objects.get(symbol=balance["asset"], exchange=exchange_obj)
                        if not Balance.objects.filter(currency=currency,exchange=exchange_obj,user=self.user).exists():
                            new_balance = Balance()
                            new_balance.user = self.user
                            new_balance.currency = currency
                            new_balance.exchange = exchange_obj
                            new_balance.value = balance['tradable']
                            new_balance.save()
                        else:
                            Balance.objects.filter(currency=currency,exchange=exchange_obj,user=self.user).update(amount=balance["tradable"])
                    except:
                        pass

        exchanges = {}
        if self.binance_api_key:
            exchanges['binance'] = {'api_key':self.binance_api_key, 'secret_key':self.binance_secret_key}
        if self.hitbtc_api_key:
            exchanges['hitbtc'] = {'api_key':self.hitbtc_api_key, 'secret_key':self.hitbtc_secret_key}
        if self.poloniex_api_key:
            exchanges['poloniex'] = {'api_key':self.poloniex_api_key, 'secret_key':self.poloniex_secret_key}

        manager = ClientManager(**exchanges)
        for exchange in exchanges.keys():
            exchange_obj = Exchange.objects.get(name__iexact=exchange)
            Thread(target=assign_balance, args=[exchange_obj]).start()

    def generate_pl_sheet(self):
        """ Iterates through trades using FIFO method to caluclate profit loss """

        exchanges = []
        if self.binance_api_key:
            exchanges.append("Binance")
        if self.hitbtc_api_key:
            exchanges.append("HitBTC")
        if self.poloniex_api_key:
            exchanges.append("Poloniex")

        profit_loss = 0

        for exchange in exchanges:
            trades = list(Trade.objects.filter(user=self.user,currency_pair__base__exchange__name=exchange))
            trades = sorted(trades, key=lambda k: k.time)

            for trade in trades[:]:
                try:
                    sell = next(item for item in trades[:] if item.type == "sell")
                    quantity = sell.quantity
                    for trade in trades[:]:
                        try:
                            buy = next(item for item in trades[:] if item.type == "buy" and item.currency_pair==sell.currency_pair)
                            if buy:
                                print("buy")
                                if quantity <= buy.quantity:
                                    if sell.usd_value > buy.usd_value:
                                        profit_loss += sell.usd_value - buy.usd_value
                                    else:
                                        profit_loss -= buy.usd_value - sell.usd_value
                                    trades.remove(sell)

                                else:
                                    quantity -= buy.quantity
                                trades.remove(buy)

                        except:
                            # print(trade.time,trade.type)
                            bought.append(trade.usd_value)
                except:
                    pass

            if profit_loss == 0:
                print("Cannot track deposit to you account")


            print(exchange)

            print(profit_loss)


class Trade(models.Model):
    """ DB model used to store users trades on exchanges"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency_pair = models.ForeignKey(CurrencyPair, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    price = models.FloatField(default=0)
    type = models.CharField(max_length=10,default="")
    time = models.DateTimeField(default=None,null=True)
    usd_value = models.FloatField(default=0)

    def get_entry_price(self):
        """ Caluclates USD value at time of trade"""

        exchange = self.currency_pair.base.exchange
        exchanges= {}
        quotes = ["USDT","USDC","USD"]
        found_match = False
        if self.user.profile.binance_api_key:
            exchanges['binance'] = {'api_key':self.user.profile.binance_api_key, 'secret_key':self.user.profile.binance_secret_key}
        if self.user.profile.hitbtc_api_key:
            exchanges['hitbtc'] = {'api_key':self.user.profile.hitbtc_api_key, 'secret_key':self.user.profile.hitbtc_secret_key}
        if self.user.profile.poloniex_api_key:
            exchanges['poloniex'] = {'api_key':self.user.profile.poloniex_api_key, 'secret_key':self.user.profile.poloniex_secret_key}
        manager = ClientManager(**exchanges)
        for exchange in exchanges.keys():
            exchange = Exchange.objects.get(name__iexact=exchange)
            if self.currency_pair.quote.name != "USD":
                for quote in quotes:
                    if CurrencyPair.objects.filter(symbol=self.currency_pair.quote.name+quote,quote__exchange=exchange).exists():
                        base = self.currency_pair.quote.name
                        try:
                            price = manager.get_historic_usd_price(exchange.name.lower(),base,quote,str(self.quantity),str(int(self.time.timestamp())))*self.price
                            print(self.currency_pair,price)
                            found_match = True
                            break
                        except:
                            pass

                if not found_match:
                    if CurrencyPair.objects.filter(symbol=self.currency_pair.quote.name+"BTC",quote__exchange=exchange).exists():
                        conversion_base = self.currency_pair.quote.name
                        conversion_quote = "BTC"
                        for quote in quotes:
                            if CurrencyPair.objects.filter(symbol="BTC"+quote,quote__exchange=exchange).exists():
                                try:
                                    conversion_price = manager.get_historic_usd_price(exchange.name.lower(),conversion_base,conversion_quote,str(self.quantity),str(int(self.time.timestamp())))
                                    price = manager.get_historic_usd_price(exchange.name.lower(),"BTC",quote,str(self.quantity),str(int(self.time.timestamp())))*conversion_price
                                    print(self.currency_pair,price)
                                    found_match = True
                                    break
                                except:
                                    price = 0
                    else:
                        price = 0

                self.usd_value = price
            else:
                self.usd_value = 1

            self.save()

    def __str__(self):
        return str(self.time)



class Balance(models.Model):
    """ DB model used to store users Balances on exchanges"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    usd_value = models.FloatField(default=0)

class TaxSheet(models.Model):
    """ DB model used to store users profit/loss data from past trades"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    basis = models.FloatField(default=0)
    outcome = models.FloatField(default=0)
    date_created = models.DateTimeField(default=datetime.now,null=True)


@receiver(post_save, sender=User)
def my_callback(instance, *args, **kwargs):
    """ Creates Profile instance for newly created User instance after saving user for the first time """

    if not Profile.objects.filter(user=instance).exists():
        profile = Profile()
        profile.user = instance
        profile.save()

@receiver(post_save, sender=Balance)
def my_callback(instance, *args, **kwargs):
    """ Saves USD value of balance after balance instance is saved """
    instance.usd_value = instance.currency.get_usd_value() * instance.amount
    instance.save()
