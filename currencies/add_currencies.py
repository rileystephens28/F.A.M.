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

""" This script pulls individial cryptocurrencies and currency currency pairs from
    all exchanges and saves them to DB"""

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
