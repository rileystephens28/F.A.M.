import os, sys,time
dir_path = str(os.path.dirname(os.path.realpath(__file__)))
dir_path = dir_path[:-14]
sys.path.insert(0, dir_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'FAM.settings'
from django.conf import settings
import django
django.setup()

from exchanges.models import Exchange
from currencies.models import Currency, CurrencyPair
from exchanges.apis.manager import WebSocketMananger
from accounts.models import Balance

""" Pulls all currencies that user have a balance in and begins streaming them on the exchanges   """

symbols = [item.currency for item in Balance.objects.all() if item.currency.symbol != "USDT" or item.currency.symbol != "USDC"]

stream_symbols = []
for symbol in symbols:
    if CurrencyPair.objects.filter(symbol=symbol.symbol+"USDC",base__exchange=symbol.exchange).exists():
        stream_symbols.append(CurrencyPair.objects.get(symbol=symbol.symbol+"USDC",base__exchange=symbol.exchange).symbol)
    if CurrencyPair.objects.filter(symbol=symbol.symbol+"USDT",base__exchange=symbol.exchange).exists():
        stream_symbols.append(CurrencyPair.objects.get(symbol=symbol.symbol+"USDT",base__exchange=symbol.exchange).symbol)
    if CurrencyPair.objects.filter(symbol=symbol.symbol+"USD",base__exchange=symbol.exchange).exists():
        stream_symbols.append(CurrencyPair.objects.get(symbol=symbol.symbol+"USD",base__exchange=symbol.exchange).symbol)
    if CurrencyPair.objects.filter(symbol=symbol.symbol+"BTC",base__exchange=symbol.exchange).exists():
        stream_symbols.append(CurrencyPair.objects.get(symbol=symbol.symbol+"BTC",base__exchange=symbol.exchange).symbol)
    if CurrencyPair.objects.filter(symbol="BTCUSDT",base__exchange=symbol.exchange).exists():
        stream_symbols.append(CurrencyPair.objects.get(symbol="BTCUSDT",base__exchange=symbol.exchange).symbol)
    elif CurrencyPair.objects.filter(symbol="BTCUSDC",base__exchange=symbol.exchange).exists():
        stream_symbols.append(CurrencyPair.objects.get(symbol="BTCUSDC",base__exchange=symbol.exchange).symbol)
    elif CurrencyPair.objects.filter(symbol="BTCUSD",base__exchange=symbol.exchange).exists():
        tream_symbols.append(CurrencyPair.objects.get(symbol="BTCUSD",base__exchange=symbol.exchange).symbol)

stream_symbols = list(set(stream_symbols))
for sym in stream_symbols:
    print(sym)
manager = WebSocketMananger(list(set(stream_symbols)))
manager.start()
