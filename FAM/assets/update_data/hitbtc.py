import json
import requests
import datetime
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
        if days < 1:
            days = 1
        params = {"period":"H1","limit":days*24}
        url = 'https://api.hitbtc.com/api/2/public/candles/'+ symbol.upper()
        candle_data = requests.get(url ,params = params).json()
        for candle in candle_data:
            candle["time"] = candle.pop("timestamp")
            candle["time"] = datetime.datetime.strptime(candle["time"],"%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%dT%H:%M:%S")
        candle_data = sorted(candle_data, key = lambda x: datetime.datetime.strptime(x["time"],"%Y-%m-%dT%H:%M:%S"))
        return json.dumps(candle_data)

#hitbtc = HitBTC()
#hitbtc.get_candlestick("ETHBTC",7)
