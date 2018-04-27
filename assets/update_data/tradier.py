import requests
import json
from datetime import datetime, timedelta
from assets.update_data.sourceAPI import SourceAPI
from sources.models import StockExchange, OptionExchange

class Tradier(SourceAPI):

    TRADIER_API_KEY = 'XCp8C02gIfnzIW99aTTU4jnPQGVJ'
    headers = {'Authorization':'Bearer ' + TRADIER_API_KEY, 'Accept':'application/json'}

    def get_tradeable_assets(self):
        url = 'https://api.tradier.com/v1/markets/lookup'
        params = {'types':'stock,etf,index','exchanges':'Q,N,P,B','linebreak':'true'}
        assets_data = requests.get(url, headers=self.headers, params=params).json()
        assets = assets_data["securities"]["security"][:10000]
        return assets

    def get_ticker(self,symbol):
        url = 'https://api.tradier.com/v1/markets/quotes'
        params = {"symbols":symbol}
        try:
            ticker_data = requests.get(url, headers=self.headers, params=params).json()
            return ticker_data["quotes"]["quote"]
        except:
            return []

    def get_all_tickers(self):
        all_assets = []
        assets = list([item["symbol"] for item in self.get_tradeable_assets()])
        assets = assets[:10000]
        counter = 0
        while len(assets[counter*100:counter*100+100]) == 100:
            symbol_str = ",".join(assets[counter*100:counter*100+100])
            all_assets += self.get_ticker(symbol_str)
            counter += 1
        symbol_str = ",".join(assets[counter*100:counter*100+100])
        all_assets += self.get_ticker(symbol_str)
        return all_assets

    def get_candlestick(self,symbol,days):
        if days < 1:
            days = 1
        today = datetime.now()
        start = (today - timedelta(days=days)).strftime("%Y-%m-%d %H-%M")
        url = 'https://api.tradier.com/v1/markets/timesales'
        params = {"symbol":symbol,'interval':'15min','session_filter':'all','start':start}
        candle_data = requests.get(url, headers=self.headers, params=params).json()["series"]["data"]
        candle_data = sorted(candle_data, key = lambda x: datetime.strptime(x["time"],"%Y-%m-%dT%H:%M:%S"))
        return json.dumps(candle_data)

    def get_option_expirations(self,symbol):
        url = 'https://api.tradier.com/v1/markets/options/expirations'
        params = {"symbol":symbol}
        exp_data = requests.get(url, headers=self.headers, params=params).json()
        return exp_data['expirations']['date']

    def get_option_chain(self,symbol,expiration):
        url = 'https://api.tradier.com/v1/markets/options/chains'
        params = {'symbol':symbol,'expiration':expiration}
        option_data = requests.get(url, headers=self.headers, params=params).json()
        return option_data["options"]["option"]
