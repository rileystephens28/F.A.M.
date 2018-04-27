import time
import sys
import os
dir_path = str(os.path.dirname(os.path.realpath(__file__)))
dir_path = dir_path[:-8]
sys.path.insert(0, dir_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'FAM.settings'
from django.conf import settings
import django
django.setup()
from accounts.models import Account
from assets.models import Stock, Option, Cryptocurrency

def get_symbols():
    symbols = []
    for account in Account.objects.filter():
        for key in account.get_all_investments().keys():
            if key not in symbols:
                symbols.append(key)
    return symbols

while True:
    try:
        symbols = get_symbols()
        for symbol in symbols:
            if Stock.objects.filter(symbol = symbol):
                asset = Stock.objects.get(symbol = symbol)
            elif Cryptocurrency.objects.filter(symbol = symbol):
                asset = Cryptocurrency.objects.get(symbol = symbol)
            else:
                asset = None
            if asset:
                asset.update_data()
        for account in Account.objects.all():
            account.update_chart()
            account.update_current_balance()
        time.sleep(2)
    except:
        print(sys.exc_info())
        time.sleep(4)
