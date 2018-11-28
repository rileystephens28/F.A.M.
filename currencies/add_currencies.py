import os, sys,time
dir_path = str(os.path.dirname(os.path.realpath(__file__)))
dir_path = dir_path[:-10]
sys.path.insert(0, dir_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'FAM.settings'
from django.conf import settings
import django
django.setup()

from exchanges.models import Exchange
from currencies.models import Currency, CurrencyPair
from exchanges.apis.manager import ClientManager

# exchanges = list(Exchange.objects.all())
exchanges = ["Binance","HitBTC","Poloniex"]
keys={'binance':{'api_key':'DoISpHGHMG6HsH3q57LmgntGO7TVMYIayzjr2DEaEPaofx4VWbaoVho4W6rwf0e7','secret_key':'DnMYU4nBguMpx2QF6BWgfaAODjJMTFmwNo6oOGcPKbb5x2HjQqBu9m3MnjDBDkBx'},
      'hitbtc':{'api_key':'25bade92584eb6d27ff04580a6e28d4d','secret_key':'53ba7dc9d5c5937620043c6f447a9db1'},
      'poloniex':{'api_key':'27V94U3F-VAWLK2EK-PJPRQ9A7-JNC9ZE5S','secret_key':'149c069085f1a32f103b09179d616c6cce67fbba0128e8e529f9500ac83f388cd61a8e82d17e3c824acd36bf1edd30d0a5479a467f810b0baa0bedbac260a212'}}

client = ClientManager(**keys)
for exchange in exchanges:
    print(exchange)
    exchange = Exchange.objects.get(name=exchange)
    currencies = client.get_currencies(exchange.name.lower())
    for currency in currencies:
        if not Currency.objects.filter(symbol=currency,exchange=exchange).exists():
            new_currency = Currency()
            new_currency.exchange = exchange
            new_currency.symbol = currency
            if currency == "USDT" or currency == "USDC":
                new_currency.name = "USD"
            else:
                new_currency.name = currency
            new_currency.save()

for exchange in exchanges:
    exchange = Exchange.objects.get(name=exchange)
    currency_pairs = client.get_currency_pairs(exchange.name.lower())
    for currency_pair in currency_pairs:
        base = Currency.objects.get(symbol=currency_pair['base'],exchange=exchange)
        quote = Currency.objects.get(symbol=currency_pair['quote'],exchange=exchange)
        if not CurrencyPair.objects.filter(base=base,quote=quote).exists():
            if exchange.name == "Poloniex":
                print("adding poloniex pair")
            new_currency = CurrencyPair()
            new_currency.base = base
            new_currency.quote = quote
            new_currency.symbol = base.symbol + quote.symbol
            new_currency.save()
