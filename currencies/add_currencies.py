import os, sys,time
dir_path = str(os.path.dirname(os.path.realpath(__file__)))
dir_path = dir_path[:-10]
sys.path.insert(0, dir_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'CryptoTrader.settings'
from django.conf import settings
import django
django.setup()

from exchanges.models import Exchange
from currencies.models import Currency, CurrencyPair
from exchanges.API.manager import ClientManager

exchanges = list(Exchange.objects.all())
client = ClientManager()
for exchange in exchanges:
    print(exchange.name)
    print("")
    currencies = client.get_currencies(exchange.name)
    for currency in currencies:
        #print(currency)
        if not Currency.objects.filter(name=currency,exchange=exchange):
            new_currency = Currency()
            new_currency.exchange = exchange
            new_currency.symbol = currency
            if currency == "USDT":
                new_currency.name = "USD"
            else:
                new_currency.name = currency
            new_currency.save()
            time.sleep(.1)

for exchange in exchanges:
    print(exchange.name)
    print("")
    currency_pairs = client.get_currency_pairs(exchange.name)
    for currency_pair in currency_pairs:
        print(currency)
        if not CurrencyPair.objects.filter(,exchange=exchange):
            wfee = client.get_withdraw_fee(exchange.name,currency)
            if wfee:
                new_currency = Currency()
                new_currency.exchange = exchange
                new_currency.name = currency
                new_currency.withdraw_fee = wfee["withdraw_fee"]
                new_currency.save()
                time.sleep(.1)




# Add currencies for binance
# Add currencies for poloniex
# Add currencies for hitbtc
# Add currencies for coinbase
