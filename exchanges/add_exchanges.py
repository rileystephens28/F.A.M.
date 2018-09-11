import sys
import os
dir_path = str(os.path.dirname(os.path.realpath(__file__)))
dir_path = dir_path[:-7]
sys.path.insert(0, dir_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'FAM.settings'
import django
django.setup()
from exchanges.models import Exchange

""" Add all cryptocurrency exchanges to CryptoExchange Database """
def add_cryptoExchange(name):
    exchange = Exchange()
    exchange.name = name
    exchange.save()

crypto_exchanges = Exchange.objects.all()
exchanges = list((item.name for item in crypto_exchanges))

if "HitBTC" not in exchanges:
    add_cryptoExchange("HitBTC")

if "Coinbase" not in exchanges:
    add_cryptoExchange("Coinbase")

if "Gemini" not in exchanges:
    add_cryptoExchange("Gemini")

if "Poloniex" not in exchanges:
    add_cryptoExchange("Poloniex")

if "Binance" not in exchanges:
    add_cryptoExchange("Poloniex")
