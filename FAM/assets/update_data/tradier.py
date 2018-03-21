import requests
from requests.adapters import HTTPAdapter
import ujson as json
import sys
sys.path.insert(0, "/home/riley_stephens/Django/FAM/FAM")
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FAM.settings")
from django.utils import timezone
import django
django.setup()
from FAM.update_data.sourceAPI import SourceAPI
from sources.models import StockExchange, OptionExchange
from options.models import Option
from stocks.models import Stock
import time
import datetime
import threading

class Tradier(SourceAPI):

    TRADIER_API_KEY = 'XCp8C02gIfnzIW99aTTU4jnPQGVJ'

    def get_tradeable_assets(self):
        url = 'https://api.tradier.com/v1/markets/lookup'
        params = {'types':'stock,etf,index','linebreak':'true'}
        r = s.get(url, params=params)
        content = json.loads(r.text)
        stocks = Stock.objects.all()
        stocks = [item.symbol for item in stocks]
        for stock in content["securities"]["security"]:
            if stock["symbol"] not in stocks:
                new_stock = Stock()
                new_stock.symbol = stock["symbol"]
                new_stock.company = stock["description"]
                if StockExchange.objects.filter(code=stock["exchange"]):
                    new_stock.exchange = StockExchange.objects.get(code=stock["exchange"])
                    new_stock.bid = 0
                    new_stock.ask = 0
                    new_stock.last = 0
                    new_stock.price = 0
                    new_stock.save()
        stocks = Stock.objects.all()
        stocks = [item.symbol for item in stocks]
        return stocks

    def get_data(self):
        pass

    def get_all_data(self):
        pass

    def getOptionExpirations(self,symbol):
        url = 'https://api.tradier.com/v1/markets/options/expirations'
        params = {'symbol':symbol}
        r = s.get(url, params=params)
        j = json.loads(r.text)
        expirations = []
        for expiration in j['expirations']['date']:
            expirations.append(expiration)
        return expirations

    def getOptionChain(self,symbol,expiration):
        url = 'https://api.tradier.com/v1/markets/options/chains'
        params = {'symbol':symbol,'expiration':expiration}
        r = s.get(url, params=params)
        j = json.loads(r.text)
        symbols = []
        for option in j['options']['option']:
            symbols.append(option['symbol'])
        return symbols

    def getSessionID(self):
        url = 'https://api.tradier.com/v1/markets/events/session'
        r = s.post(url)
        j = json.loads(r.text)
        sessionid = j['stream']['sessionid']
        return sessionid

    def stream_data(self,session_id,symbols):
        url = 'https://stream.tradier.com/v1/markets/events'
        params = {'sessionid':session_id,'linebreak':'true','filter':'trade,timesale,summary','symbols':symbols}
        #'filter':'trade',
        r = s.post(url,data=params,stream=True)
        #print(r.status_code)
        print("Opening stream...")
        for line in r.iter_lines():
            if line: # filter out keep-alive new lines
                if "is not a valid symbol" in str(line):
                    line = str(line)
                    print(str(line))
                    symbol = symbol.replace("b'","")
                    symbol = symbol.replace("'","")
                    symbol = line.replace(" is not a valid symbol","")
                    print (symbol)
                    bad_stock = Stock.objects.get(symbol = symbol)
                    bad_stock.delete()
                    print("Just deleted %s from database" % bad_stock)
                data = json.loads(line)
                if data["type"] != "option"
                    try:
                        self.parse_stock(data)
                    except:
                        print(sys.exc_info())
                        print(data)
                else:
                    try:
                        self.parse_option(data)
                    except:
                        print(sys.exc_info())
                        print(data)

    def parse_stock(self, data):
            if Stock.objects.get(symbol=data["symbol"]):
                stock = Stock.objects.get(symbol=data["symbol"])
            else:
                stock = Stock()
                stock.symbol = data["symbol"]
            if data["type"] == "trade":
                if data["price"] != "" and data["price"] != 'NaN':
                    stock.price = data["price"]
                else:
                    stock.price = 0
                if data["cvol"] != "" and data["cvol"] != 'NaN':
                    stock.volume = data["cvol"]
                else:
                    stock.volume = 0
                if data["last"] != "" and data["last"] != 'NaN':
                    stock.last = data["last"]
                else:
                    stock.last = 0
            elif data["type"] == "timesale":
                if data["bid"] != "" and data["bid"] != 'NaN':
                    stock.bid = data["bid"]
                else:
                    stock.bid = 0
                if data["ask"] != "" and data["ask"] != 'NaN':
                    stock.ask = data["ask"]
                else:
                    stock.ask = 0
            else:
                if data["prevClose"] != "" and data["prevClose"] != 'NaN':
                    stock.close_price = data["prevClose"]
                else:
                    stock.close_price = 0
                if data["open"] != "" and data["open"] != 'NaN':
                    stock.open_price = data["open"]
                else:
                    stock.open_price = 0
                if data["high"] != "" and data["high"] != 'NaN':
                    stock.high = data["high"]
                else:
                    stock.high = 0
                if data["low"] != "" and data["low"] != 'NaN':
                    stock.low = data["low"]
                else:
                    stock.low = 0
            stock.save()

    def parse_option(self,data):
        pass

tradier = Tradier("Tradier")
s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=1))
s.headers.update({'Authorization':'Bearer ' + tradier.TRADIER_API_KEY, 'Accept':'application/json'})
#stocks = tradier.get_tradeable_assets()
nyse = StockExchange.objects.get(name = "NYSE")
session_id = tradier.getSessionID()
#nasdq = StockExchange.objects.get(name = "Nasdaq OMX")
num_stocks = len(Stock.objects.filter(exchange=nyse))
print(num_stocks)
x = 0
total = 0
symbol_list = []
for stock in Stock.objects.filter(exchange=nyse):
    if num_stocks - total > 100:
        if x == 100:
            symbol_str = ",".join(symbol_list)
            t = threading.Thread(target=tradier.stream_data, args=(session_id,symbol_str))
            t.start()
            x = 0
            symbol_list = []
        else:
            symbol_list.append(stock.symbol)
            x += 1
    elif total == num_stocks:
        symbol_str = ",".join(symbol_list)
        t = threading.Thread(target=tradier.stream_data, args=(session_id,symbol_str))
        t.start()
        x = 0
        symbol_list = []
    else:
        symbol_list.append(stock.symbol)
    total += 1
