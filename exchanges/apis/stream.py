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
from exchanges.apis.manager import ClientManager
from accounts.models import Balance

symbols = [item.currency for item in Balance.objects.filter() if item.current.symbol != "USDT" or item.current.symbol != "USDC"]
stream_symbols = []
for symbol in symbols:
    if CurrencyPair.objects.filter(base=symbol,quote=)
print(symbols)
