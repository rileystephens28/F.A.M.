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

tradier = Tradier()
stocks = tradier.get_all_tickers()
saved = list([item.symbol for item in Stock.objects.all()])
for stock in stocks:
    if stock["symbol"] not in saved:
        new_stock = Stock()
        new_stock.symbol = stock["symbol"]
        new_stock.exchange = StockExchange.objects.get(code=stock["exch"])
        new_stock.bid = 0
        new_stock.ask = 0
        new_stock.last = 0
        new_stock.save()

hitbtc = HitBTC()
cryptos = hitbtc.get_tradeable_assets()
saved = list([item.symbol for item in Cryptocurrency.objects.all()])
exchange = CryptoExchange.objects.get(name="HitBTC")
for crypto in cryptos:
    if crypto["id"] not in saved:
        new_crypto = Cryptocurrency()
        new_crypto.base = crypto["baseCurrency"]
        new_crypto.quote = crypto["quoteCurrency"]
        new_crypto.symbol = crypto["id"]
        new_crypto.exchange = exchange
        new_crypto.save()
