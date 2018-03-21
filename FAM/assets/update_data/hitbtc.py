import asyncio
import websockets
import json
import threading
import requests
import time
import resource
#import datetime
import sys
sys.path.insert(0, "/home/riley_stephens/Django/FAM/FAM")
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FAM.settings")
from django.utils import timezone
import django
django.setup()
from cryptocurrencies.models import Cryptocurrency
from FAM.update_data.sourceAPI import SourceAPI
from sources.models import CryptoExchange

class HitBTC(SourceAPI):

    def get_tradeable_assets(self):

        data = requests.get('https://api.hitbtc.com/api/2/public/symbol').json()
        currency_pairs = []
        exchange = CryptoExchange.objects.get(name="HitBTC")

        for pairs in data:
            if not Cryptocurrency.objects.filter(base=pairs['baseCurrency'],quote=pairs['quoteCurrency'],exchange=exchange):
                pair = Cryptocurrency()
                pair.base = pairs["baseCurrency"]
                pair.quote = pairs["quoteCurrency"]
                pair.exchange = exchange
                pair.save()

            currency_pairs.append([pairs["baseCurrency"],pairs["quoteCurrency"]])

        return currency_pairs

    def get_data(self, base, quote):
        symbol = base + quote
        ticker_data = requests.get('https://api.hitbtc.com/api/2/public/ticker/' + symbol.upper()).json()
        try:
            ticker = {}
            ticker["symbol"] = ticker_data["symbol"]
            ticker["bid"] = ticker_data["bid"]
            ticker["ask"] = ticker_data["ask"]
            ticker["last"] = ticker_data["last"]
            ticker["base_vol"] = ticker_data["volume"]
            ticker["quote_vol"] = ticker_data["volumeQuote"]

            return ticker
        except:
            return "Currency pair not found"

    def get_all_data(self):

        pairs = self.get_tradeable_assets()
        tickers = requests.get('https://api.hitbtc.com/api/2/public/ticker').json()

        for ticker in tickers:
            for pair in pairs:
                if ticker['symbol'] == pair[0] + pair[1]:
                    currency_pair = Cryptocurrency()
                    currency_pair.base = pair[0]
                    currency_pair.quote = pair[1]
                    currency_pair.exchange = CryptoExchange.objects.get(name = "hitbtc")

                    if ticker["bid"] != None:
                        currency_pair.bid =  float(ticker["bid"])
                    else:
                        currency_pair.bid = 0
                    if ticker["ask"] != None:
                        currency_pair.ask =  float(ticker["ask"])
                    else:
                        currency_pair.ask = 0

                    currency_pair.last = ticker["last"]
                    currency_pair.base_volume = ticker["volume"]
                    currency_pair.quote_volume = ticker["volumeQuote"]
                    currency_pair.save()


    async def stream_data(self, loop, symbol,id):
        #symbol must be in the form of currency pair ex: [ETH,BTC]
        exchangeID = CryptoExchange.objects.get(name="HitBTC").id
        if Cryptocurrency.objects.filter(base=symbol[0],quote=symbol[1], exchange_id = exchangeID):
            currency = Cryptocurrency.objects.get(base=symbol[0],quote=symbol[1], exchange_id = exchangeID)
        elif CurrencyPair.objects.filter(base=symbol[0],quote=symbol[1], exchange_id = exchangeID):
            currency = Cryptocurrency()
            currency.base = symbol[0]
            currency.quote = symbol[1]
            currency.exchange_id = exchangeID

        print((symbol[0]+symbol[1]).upper())

        url = 'wss://api.hitbtc.com/api/2/ws'
        async with websockets.connect(url, loop = loop) as websocket:
            await websocket.send('{"method": "subscribeTicker","params": {"symbol": "'+(symbol[0]+symbol[1]).upper()+'","period": "M1"},"id": "'+id+'"}')
            response = await websocket.recv()
            #print (response)

            while True:
                ticker = await websocket.recv()
                ticker = json.loads(ticker)
                if ticker['params']["bid"] != None:
                    currency.bid = ticker['params']["bid"]
                else:
                    currency.bid = 0.00000000
                if ticker['params']["ask"] != None:
                    currency.ask = ticker['params']["ask"]
                else:
                    currency.ask = 0.00000000
                if ticker['params']["last"] != None:
                    currency.last = ticker['params']["last"]
                else:
                    currency.last = 0.00000000
                currency.base_volume = ticker['params']["volume"]
                currency.quote_volume = ticker['params']["volumeQuote"]
                currency.last_updated = ticker['params']["timestamp"]
                currency.save()
                #print("Updated " + (symbol[0]+symbol[1]).upper() + " at " + currency.last_updated)

def start_stream(symbol,obj):
    loop = asyncio.new_event_loop()
    loop.run_until_complete(obj.stream_data(loop, symbol,'123'))
    print("Opening stream on " + symbol[0] + symbol[1])

def main():
    resource.setrlimit(resource.RLIMIT_NOFILE,(10000,10000))
    hitbtc = HitBTC("HitBTC")
    hitbtc.get_tradeable_assets()

    all_pairs = Cryptocurrency.objects.all()
    for pair in all_pairs:
        t = threading.Thread(target=start_stream, args=([pair.base,pair.quote],hitbtc))
        t.start()
    print("Done")
        #time.sleep(.5)
    #hitbtc.get_tradeable_assets()


main()
