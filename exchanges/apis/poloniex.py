import json
import hmac
import time
import hashlib
import requests
import itertools
import threading
from datetime import datetime
from django.db import connection, connections
from exchanges.models import Exchange
from currencies.models import Currency, CurrencyPair
from exchanges.apis.websocket_utils import WebSocket, StreamingError

class PoloniexClient:
    """Client to connect to Poloniex public and private APIs."""

    public_url='https://poloniex.com/public'
    private_url='https://poloniex.com/tradingApi'

    class _PoloniexAuth(requests.auth.AuthBase):
        """Poloniex Request Authentication. Consider replacing this class with regualar class method"""

        def __init__(self,api_key,secret_key):
            self._apikey = api_key
            self._secret = secret_key

        def __call__(self, request):
            signature = hmac.new(
                str.encode(self._secret, 'utf-8'),
                str.encode(request.body, 'utf-8'),
                hashlib.sha512
            )
            request.headers.update({"Key": self._apikey,
                                    "Sign": signature.hexdigest()})
            return request

    def __init__(self, api_key,secret_key,nonce_iter=None,nonce_lock=None):
        """Initialize the Poloniex client."""
        self._apikey = api_key
        self._secret = secret_key
        self.session = requests.Session()
        self.nonce_lock = nonce_lock or threading.RLock()
        self.nonce_iter = nonce_iter or itertools.count(int(time.time() * 1000000000))

    def _public(self, command, **params):
        """Invoke the 'command' public API with optional params."""
        params['command'] = command
        response = self.session.get(self.public_url, params=params)
        try:
            return json.loads(response.text)
        except:
            return {}

    def _private(self, command, **params):
        """Invoke the 'command' public API with optional params."""
        if not self._apikey or not self._secret:
            raise PoloniexCredentialsException('missing apikey/secret')

        with self.nonce_lock:
            params.update({'command': command, 'nonce': next(self.nonce_iter)})
            response = self.session.post(
                self.private_url, data=params,
                auth=self._PoloniexAuth(self._apikey, self._secret))
            try:
                return json.loads(response.text)
            except:
                return {}

#-------------------
# Private API Methods
#-------------------

    def get_currencies(self):
        """Returns information about currencies."""
        return list(set(self._public('returnCurrencies').keys()))

    def get_currency_pairs(self):
        currency_pairs = []
        products = list(self._public('returnTicker').keys())
        for product in products:
            base = product.split("_")[1]
            quote = product.split("_")[0]
            currency_pair = base + quote
            currency_pairs.append({"currency_pair":currency_pair,"base":base,"quote":quote})
        return currency_pairs

    def get_balance(self,asset):
        """Returns all of your available balances."""
        response = self._private('returnBalances')
        asset = asset.upper()
        tradable = float(response[asset])
        return {"asset":asset,"tradable":tradable,"locked":0.0}


    def get_balances(self):
        """Returns all of your available balances."""
        balances = []
        response = self._private('returnBalances')
        for key,val in response.items():
            asset = key.upper()
            tradable = float(val)
            balances.append({"asset":asset,"tradable":tradable,"locked":0.0})
        return balances

    def get_trade_history(self, base, quote, limit=500):
        """Returns your trade history for a given market, specified by the
        "currencyPair" POST parameter. You may specify "all" as the
        currencyPair to receive your trade history for all markets. You may
        optionally specify a range via "start" and/or "end" POST parameters,
        given in UNIX timestamp format; if you do not specify a range, it will
        be limited to one day."""
        start = 0
        end = int(time.time())
        symbol = quote.upper() + "_" + base.upper()    # reverse order of normal
        orders = []
        response = self._private('returnTradeHistory', currencyPair=symbol,start=start, end=end, limit=limit)
        for order in response:
            symbol = base.upper() + quote.upper()
            id = order["tradeID"]
            price = float(order["rate"])
            amount = float(order["amount"])
            time = datetime.strptime(order["date"],"%Y-%m-%d %H:%M:%S")
            type = order["type"]
            orders.append({"symbol":symbol,"id":id,"time":time,"price":price,"amount":amount,"type":type})
        return orders

    def get_deposit_history(self,asset):
        """Returns your deposit history within a range, specified by the
        "start" and "end" POST parameters, both of which should be given as
        UNIX timestamps."""
        start = 0
        end = int(time.time())
        deposits = []
        response = self._private('returnDepositsWithdrawals', start=start, end=end)['deposits']
        for deposit in response:
            if deposit["currency"] == asset.upper():
                asset = deposit["currency"]
                time = datetime.fromtimestamp(int(deposit["timestamp"]))
                amount = deposit["amount"]
                address = deposit["address"]
                status = "Complete" if deposit["status"] == "COMPLETE" else "Pending"
                deposits.append({"asset":asset,"time":time,"amount":amount,"address":address,"status":status})
        return deposits

    def get_withdraw_history(self,asset):
        """Returns your withdrawal history within a range, specified by the
        "start" and "end" POST parameters, both of which should be given as
        UNIX timestamps."""
        start = 0
        end = int(time.time())
        withdraws = []
        response = self._private('returnDepositsWithdrawals', start=start, end=end)['withdrawals']
        for withdraw in response:
            if withdraw["currency"] == asset.upper():
                asset = withdraw["currency"]
                time = datetime.fromtimestamp(int(withdraw["timestamp"]))
                amount = withdraw["amount"]
                address = withdraw["address"]
                status = "Complete" if withdraw["status"] == "COMPLETE" else "Pending"
                withdraws.append({"asset":asset,"time":time,"amount":amount,"address":address,"status":status})
        return withdraws



#-------------------
# Streaming Classes
#-------------------

class PoloniexWebsocket(WebSocket):

    url = "wss://api2.poloniex.com:443"

    currency_codes = {7:'BTC_BCN',14:'BTC_BTS',15:'BTC_BURST',20:'BTC_CLAM',24:'BTC_DASH',25:'BTC_DGB',
                      27:'BTC_DOGE',38:'BTC_GAME',43:'BTC_HUC',50:'BTC_LTC',51:'BTC_MAID',58:'BTC_OMNI',
                      61:'BTC_NAV',64:'BTC_NMC',69:'BTC_NXT',75:'BTC_PPC',89:'BTC_STR',92:'BTC_SYS',
                      97:'BTC_VIA',100:'BTC_VTC',108:'BTC_XCP',112:'BTC_XEM',114:'BTC_XMR',116:'BTC_XPM',
                      117:'BTC_XRP',121:'USDT_BTC',122:'USDT_DASH',123:'USDT_LTC',124:'USDT_NXT',125:'USDT_STR',
                      126:'USDT_XMR',127:'USDT_XRP',129:'XMR_BCN',132:'XMR_DASH',137:'XMR_LTC',138:'XMR_MAID',
                      140:'XMR_NXT',148:'BTC_ETH',149:'USDT_ETH',150:'BTC_SC',155:'BTC_FCT',162:'BTC_DCR',
                      163:'BTC_LSK',166:'ETH_LSK',167:'BTC_LBC',168:'BTC_STEEM',169:'ETH_STEEM',170:'BTC_SBD',
                      171:'BTC_ETC',172:'ETH_ETC',173:'USDT_ETC',174:'BTC_REP',175:'USDT_REP',176:'ETH_REP',
                      177:'BTC_ARDR',178:'BTC_ZEC',179:'ETH_ZEC',180:'USDT_ZEC',181:'XMR_ZEC',182:'BTC_STRAT',
                      184:'BTC_PASC',185:'BTC_GNT',186:'ETH_GNT',189:'BTC_BCH',190:'ETH_BCH',191:'USDT_BCH',
                      192:'BTC_ZRX',193:'ETH_ZRX',219:'BTC_BCN',221:'BTC_BTS',224:'BTC_BURST',227:'BTC_CLAM',
                      229:'BTC_DASH',232:'BTC_DGB',235:'BTC_DOGE',238:'BTC_GAME',240:'BTC_HUC',243:'BTC_LTC',
                      246:'BTC_MAID',248:'BTC_OMNI',251:'BTC_NAV',254:'BTC_NMC',257:'BTC_NXT',259:'BTC_PPC',
                      262:'BTC_STR',265:'BTC_SYS',267:'BTC_VIA',270:'BTC_VTC',273:'BTC_XCP',276:'BTC_XEM',
                      278:'BTC_XMR',281:'BTC_XPM',284:'BTC_XRP',286:'USDT_BTC',289:'USDT_DASH',292:'USDT_LTC',
                      295:'USDT_NXT',297:'USDT_STR',300:'USDT_XMR',303:'USDT_XRP',305:'XMR_BCN',308:'XMR_DASH',
                      311:'XMR_LTC',314:'XMR_MAID',316:'XMR_NXT',319:'BTC_ETH',322:'USDT_ETH',324:'BTC_SC',
                      327:'BTC_FCT',330:'BTC_DCR',333:'BTC_LSK',335:'ETH_LSK',338:'BTC_LBC',341:'BTC_STEEM',
                      343:'ETH_STEEM',346:'BTC_SBD',349:'BTC_ETC',352:'ETH_ETC'}

    def __init__(self,symbols):
        self.symbols = symbols
        self.exchange = Exchange.objects.get(name="Poloniex")
        super().__init__()
        self.subscribe(1002)

    def subscribe(self,channel,command="subscribe"):
        # Can only subscribe to one channel per socket in think
        """1010:	Heartbeat
           1002:	Ticker
           1003:	24 hour Exchange Volume"""

        data = {"command" : command, "channel" : channel}
        self.socket.send(json.dumps(data))

    def start(self):
        while True:
            result = self.socket.recv()
            try:
                result = json.loads(result)
                if len(result) > 2:
                    t = threading.Thread(target=self.process_response,args=[result])
                    t.daemon = True
                    t.start()
            except json.decoder.JSONDecodeError: # This means nothing was received for json to decode
                self.reconnect()
                self.subscribe(1002)
            time.sleep(.3)

    def process_response(self,msg):
        symbol = self.currency_codes.get(msg[2][0])
        if symbol:
            base = symbol.split("_")[1]
            quote = symbol.split("_")[0]
            currency_pair = base + quote
            if currency_pair in self.symbols:
                # print(msg)
                bid = float(msg[2][3])
                ask = float(msg[2][2])
                last = float(msg[2][1])
                base_volume = float(msg[2][5])
                quote_volume = float(msg[2][6])
                CurrencyPair.objects.filter(symbol=currency_pair,base__exchange=self.exchange).update(bid=bid,ask=ask,last=last,base_volume=base_volume,quote_volume=quote_volume)
                connection.close()
                # print("poloniex  ", currency_pair, last) # save to database here


#-------------------
# Exception Classes
#-------------------

class PoloniexException(Exception):
    """Generic Poloniex Exception."""
    pass

class PoloniexCredentialsException(PoloniexException, RuntimeError):
    """Missing or wrong credentials while using Trading API."""
    pass

class PoloniexCommandException(PoloniexException, RuntimeError):
    """Error in command execution."""
    pass
