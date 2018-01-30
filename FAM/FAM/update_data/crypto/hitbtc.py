import requests
from cryptocurrencies import Cryptocurrency

class HitBTC(Exchange):

    def get_tradeable_pairs(self):

        data = requests.get('https://api.hitbtc.com/api/2/public/symbol').json()
        currency_pairs = []

        for pairs in data:
            currency_pairs.append([pairs["baseCurrency"],pairs["quoteCurrency"]])

        return currency_pairs

    def get_depth(self, base, quote):
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

    def get_all_depths(self):
        tickers = requests.get('https://api.hitbtc.com/api/2/public/ticker').json()
        all_tickers = {}

        for ticker in tickers:
            one_ticker = {}

            if ticker["bid"] != None:
                one_ticker["bid"] =  float(ticker["bid"])
            else:
                one_ticker["bid"] = 0
            if ticker["ask"] != None:
                one_ticker["ask"] =  float(ticker["ask"])
            else:
                one_ticker["ask"] = 0

            one_ticker["last"] = ticker["last"]
            one_ticker["base_vol"] = ticker["volume"]
            one_ticker["quote_vol"] = ticker["volumeQuote"]
            all_tickers[ticker["symbol"]] = one_ticker

        return all_tickers
