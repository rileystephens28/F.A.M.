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

symbols = [item.currency for item in Balance.objects.all() if item.currency.symbol != "USDT" or item.currency.symbol != "USDC"]

stream_symbols = []
for symbol in symbols:
    if Currency.objects.filter(symbol="USDC",exchange=symbol.exchange).exists():
        usd = Currency.objects.get(symbol="USDC",exchange=symbol.exchange)
    elif Currency.objects.filter(symbol="USDT",exchange=symbol.exchange).exists():
        usd = Currency.objects.get(symbol="USDT",exchange=symbol.exchange)
    elif Currency.objects.filter(symbol="USD",exchange=symbol.exchange):
        usd = Currency.objects.get(symbol="USD",exchange=symbol.exchange)

    if CurrencyPair.objects.filter(base=symbol,quote=usd).exists():
        stream_symbols.append(symbol.symbol+usd.symbol)

    if CurrencyPair.objects.filter(base=symbol,quote__symbol="BTC").exists():
        stream_symbols.append(symbol.symbol+"BTC")

    if Currency.objects.filter(symbol="USDC",exchange=symbol.exchange).exists():
        usd = Currency.objects.get(symbol="USDC",exchange=symbol.exchange)


stream_symbols.append('BTCUSD')
stream_symbols.append('BTCUSDC')
stream_symbols.append('BTCUSDT')
stream_symbols.append('ETHUSD')

manager = WebSocketMananger(list(set(stream_symbols)))
manager.start()
