from exchanges.apis.poloniex import PoloniexClient
from exchanges.apis.hitbtc import HitbtcClient
from exchanges.apis.binance import BinanceClient

class ClientManager:

    def __init__(self, **kwargs):
        # Need to get api keys and add them as inputs to client modules
        if 'poloniex' in kwargs.keys():
            self.poloniex = PoloniexClient(kwargs['poloniex']['api_key'],kwargs['poloniex']['secret_key'])
        if 'hitbtc' in kwargs.keys():
            self.hitbtc = HitbtcClient(kwargs['hitbtc']['api_key'],kwargs['hitbtc']['secret_key'])
        if 'binance' in kwargs.keys():
            self.binance= BinanceClient(kwargs['binance']['api_key'],kwargs['binance']['secret_key'])

    def get_currencies(self,exchange):
        exec("x = self."+exchange+".get_currencies()")
        return locals()['x']

    def get_currency_pairs(self,exchange):
        exec("x = self."+exchange+".get_currency_pairs()")
        data = locals()['x']
        return data

    def get_balances(self,exchange):
        exec("x = self."+exchange+".get_balances()")
        return locals()['x']

    def get_trade_history(self,exchange,base,quote):
        exec("x = self."+exchange+".get_trade_history('"+base+"','"+quote+"')")
        data = locals()['x']
        return data

    def get_deposit_history(self,exchange,asset):
        exec("x = self."+exchange+".get_deposit_history('"+asset+"')")
        return locals()['x']

    def get_withdraw_history(self,exchange,asset):
        exec("x = self."+exchange+".get_withdraw_history('"+asset+"')")
        return locals()['x']


class WebSocketMananger:

    def __init__(self, symbols):
        # Need to get api keys and add them as inputs to client modules
        self.poloniex = PoloniexWebsocket(symbols)
        self.hitbtc = HitbtcWebsocket(symbols)
        self.binance = BinanceWebsocket(symbols)
