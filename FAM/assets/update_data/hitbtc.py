import json
import requests
from assets.update_data.sourceAPI import SourceAPI
from sources.models import CryptoExchange

class HitBTC(SourceAPI):

    def get_tradeable_assets(self):
        return requests.get('https://api.hitbtc.com/api/2/public/symbol').json()

    def get_ticker(self, symbol):
        return requests.get('https://api.hitbtc.com/api/2/public/ticker/' + symbol.upper()).json()


    def get_all_tickers(self):
        return requests.get('https://api.hitbtc.com/api/2/public/ticker').json()

    def get_candlestick(self,symbol,days):

        params = {"period":"H1","limit":days*24}
        url = 'https://api.hitbtc.com/api/2/public/candles/'+ symbol.upper()
        candle_data = requests.get(url ,params = params).json()
        for candle in candle_data:
            candle["time"] = candle.pop("timestamp")
        candle_data = sorted(candle_data, key = lambda x: x['time'])
        for candle in candle_data:
            print(candle["time"])
        print(len(candle_data))
        return json.dumps(candle_data)

#hitbtc = HitBTC()
#hitbtc.get_candlestick("ETHBTC",7)
