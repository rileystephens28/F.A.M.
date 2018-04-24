import json
import requests
import sys
import os
dir_path = str(os.path.dirname(os.path.realpath(__file__)))
dir_path = dir_path[:-6]
sys.path.insert(0, dir_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'FAM.settings'
from django.conf import settings
import django
django.setup()
from sources.models import CryptoExchange, StockExchange
from assets.models import Stock, Option, Cryptocurrency
from assets.update_data.hitbtc import HitBTC
from assets.update_data.tradier import Tradier

def check_value(value):
    if value:
        return value
    return 0

tradier = Tradier()
stocks = tradier.get_all_tickers()
saved = list([item.symbol for item in Stock.objects.all()])
for stock in stocks:
    if stock["symbol"] not in saved:
        new_stock = Stock()
        new_stock.symbol = stock["symbol"]
        new_stock.exchange = StockExchange.objects.get(code=stock["exch"])
        new_stock.bid = check_value(stock["bid"])
        new_stock.ask = check_value(stock["ask"])
        new_stock.last = check_value(stock["last"])
        new_stock.volume = check_value(stock["volume"])
        new_stock.high = check_value(stock["high"])
        new_stock.low = check_value(stock["low"])
        new_stock.open_price = check_value(stock["open"])
        new_stock.close_price = check_value(stock["close"])
        new_stock.save()

hitbtc = HitBTC()
cryptos = hitbtc.get_all_tickers()
saved = list([item.symbol for item in Cryptocurrency.objects.all()])
exchange = CryptoExchange.objects.get(name="HitBTC")
for crypto in cryptos:
    if crypto["symbol"] not in saved:
        new_crypto = Cryptocurrency()
        new_crypto.symbol = crypto["symbol"]
        new_crypto.exchange = exchange
        new_crypto.bid = check_value(crypto["bid"])
        new_crypto.ask = check_value(crypto["ask"])
        new_crypto.last = check_value(crypto["last"])
        new_crypto.high =  check_value(crypto["high"])
        new_crypto.low =  check_value(crypto["low"])
        new_crypto.base_volume = check_value(crypto["volume"])
        new_crypto.quote_volume = check_value(crypto["volumeQuote"])
        new_crypto.save()
