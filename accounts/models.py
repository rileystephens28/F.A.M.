import time
from threading import Thread
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from currencies.models import Currency, CurrencyPair
from exchanges.models import Exchange
from exchanges.apis.manager import ClientManager

class UserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
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
        def get_trades_from_exchange():
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
                    time.sleep(.3)

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
        def assign_balance(_exchange):
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
        # balances = {}
        manager = ClientManager(**exchanges)
        for exchange in exchanges.keys():
            exchange_obj = Exchange.objects.get(name__iexact=exchange)
            Thread(target=assign_balance).start()


class Trade(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency_pair = models.ForeignKey(CurrencyPair, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    price = models.FloatField(default=0)
    type = models.CharField(max_length=10,default="")
    time = models.DateTimeField(default=None,null=True)
    usd_value = models.FloatField(default=0)


class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    usd_value = models.FloatField(default=0)

@receiver(post_save, sender=User)
def my_callback(instance, *args, **kwargs):
    if not Profile.objects.filter(user=instance).exists():
        profile = Profile()
        profile.user = instance
        profile.save()

@receiver(post_save, sender=Balance)
def my_callback(instance, *args, **kwargs):
    instance.usd_value = instance.currency.get_usd_value() * instance.amount
    instance.save()
