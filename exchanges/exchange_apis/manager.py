import sys
import os
dir_path = str(os.path.dirname(os.path.realpath(__file__)))
dir_path = dir_path[:-13]
sys.path.insert(0, dir_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'CryptoTrader.settings'
from django.conf import settings
import django
django.setup()

from currencies.models import CurrencyPair
from exchanges.models import Exchange
from exchanges.API.poloniex import PoloniexClient
from exchanges.API.hitbtc import HitbtcClient
from exchanges.API.binance import BinanceClient
from exchanges.API.config import *

class ClientManager:

    def __init__(self):
        # Need to get api keys and add them as inputs to client modules
        self.poloniex = PoloniexClient(poloniex_key,poloniex_secret)
        self.hitbtc = HitbtcClient(hitbtc_key,hitbtc_secret)
        self.binance= BinanceClient(binance_key,binance_secret)

    def get_currencies(self,exchange):
        exec("x = self."+exchange+".get_currencies()")
        data = locals()['x']
        return data

    def get_currency_pairs(self,exchange):
        exec("x = self."+exchange+".get_currency_pairs()")
        data = locals()['x']
        return data

    def get_balance(self,exchange,symbol):
        exec("x = self."+exchange+".get_balance('"+symbol+"')")
        data = locals()['x']
        return data

    def get_balances(self,exchange):
        exec("x = self."+exchange+".get_balances()")
        data = locals()['x']
        return data

    def buy(self,exchange,base,quote,price,amount):
        # Should be limit
        exec("x = self."+exchange+".buy("+base+","+quote+","+price+","+amount+")")
        data = locals()['x']
        return data

    def sell(self,exchange,base,quote,price,amount):
        # Should be limit
        exec("x = self."+exchange+".sell("+base+","+quote+","+price+","+amount+")")
        data = locals()['x']
        return data

    def cancel_order(self,exchange,orderID):
        exec("x = self."+exchange+".cancel_order("+orderID+")")
        data = locals()['x']
        return data

    def get_open_orders(self,exchange):
        exec("x = self."+exchange+".get_open_orders()")
        data = locals()['x']
        return data

    def get_deposit_address(self,exchange,asset):
        exec("x = self."+exchange+".get_deposit_address('"+asset+"')")
        data = locals()['x']
        return data

    def withdraw(self,from_exchange,to_exchange,currency,amount):
        address = self.get_deposit_address(to_exchange,asset)
        exec(self._exchange(from_exchange)+".withdraw("+asset+","+amount+","+address+")")

    def get_trade_history(self,exchange,base,quote):
        exec("x = self."+exchange+".get_trade_history('"+base+"','"+quote+"')")
        data = locals()['x']
        return data

    def get_deposit_history(self,exchange,asset):
        exec("x = self."+exchange+".get_deposit_history('"+asset+"')")
        data = locals()['x']
        return data

    def get_withdraw_history(self,exchange,asset):
        exec("x = self."+exchange+".get_withdraw_history('"+asset+"')")
        data = locals()['x']
        return data

    def get_trade_fee(self,exchange,base,quote):
        exec("x = self."+exchange+".get_trade_fee('"+base+"','"+quote+"')")
        data = locals()['x']
        return data

    def get_withdraw_fee(self,exchange,asset):
        exec("x = self."+exchange+".get_withdraw_fee('"+asset+"')")
        data = locals()['x']
        return data

    # def get_price(self,base,quote):
    #     if CurrencyPair.objects.filter(base=base,quote=quote,exchange=self.exchange).exists():
    #         return CurrencyPair.objects.filter(base=base,quote=quote,exchange=self.exchange).values("last")


class WebSocketMananger:

    def __init__(self, symbols):
        # Need to get api keys and add them as inputs to client modules
        self.poloniex = PoloniexWebsocket(symbols)
        self.hitbtc = HitbtcWebsocket(symbols)
        self.binance = BinanceWebsocket(symbols)
