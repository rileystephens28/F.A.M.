from exchanges.API.websocket_utils import WebSocket, StreamingError
from json import dumps, loads
import hmac as _hmac
import hashlib as _hashlib
import requests as _requests
import itertools as _itertools
import threading as _threading
import time as _time
from datetime import datetime

class PoloniexClient:
    """Client to connect to Poloniex public and private APIs."""

    public_url='https://poloniex.com/public'
    private_url='https://poloniex.com/tradingApi'

    class _PoloniexAuth(_requests.auth.AuthBase):

        """Poloniex Request Authentication. Consider replacing this class with regualar class method"""

        def __init__(self,api_key,secret_key):
            self._apikey = api_key
            self._secret = secret_key

        def __call__(self, request):
            signature = _hmac.new(
                str.encode(self._secret, 'utf-8'),
                str.encode(request.body, 'utf-8'),
                _hashlib.sha512
            )
            request.headers.update({"Key": self._apikey,
                                    "Sign": signature.hexdigest()})
            return request

    def __init__(self, api_key,secret_key,nonce_iter=None,nonce_lock=None):
        """Initialize the Poloniex client."""
        self._apikey = api_key
        self._secret = secret_key
        self.session = _requests.Session()
        self.nonce_lock = nonce_lock or _threading.RLock()
        self.nonce_iter = nonce_iter or _itertools.count(int(_time.time() * 1000000))

    def _public(self, command, **params):
        """Invoke the 'command' public API with optional params."""
        params['command'] = command
        response = self.session.get(self.public_url, params=params)
        try:
            return loads(response.text)
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
                return loads(response.text)
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
            base = product.split("_")[0]
            quote = product.split("_")[1]
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


    def buy(self,base,quote,rate,amount,fillOrKill=None,immediateOrCancel=None, ostOnly=None):
        """Places a limit buy order in a given market. Required POST parameters
        are "currencyPair", "rate", and "amount". If successful, the method
        will return the order number."""
        currency_pair = base.upper()+"_"+quote.upper()
        return self._private('buy', currencyPair=currency_pair, rate=rate,amount=amount,
                             fillOrKill=fillOrKill,immediateOrCancel=immediateOrCancel,postOnly=postOnly)

    def sell(self,base,quote,rate,amount,fillOrKill=None,immediateOrCancel=None, ostOnly=None):
        """Places a sell order in a given market. Parameters and output are
        the same as for the buy method."""
        currency_pair = base.upper()+"_"+quote.upper()
        return self._private('sell', currencyPair=currency_pair, rate=rate,amount=amount,
                             fillOrKill=fillOrKill,immediateOrCancel=immediateOrCancel,postOnly=postOnly)

    def cancel_order(self, orderID):
        """Cancels an order you have placed in a given market. Required POST
        parameter is "orderNumber"."""
        return self._private('cancelOrder', orderNumber=orderID)

    def get_open_orders(self, currencyPair='all'):
        """Returns your open orders for a given market, specified by the
        "currencyPair" POST parameter, e.g. "BTC_XCP". Set "currencyPair" to
        "all" to return open orders for all markets."""
        orders = []
        response = self._private('returnOpenOrders', currencyPair=currencyPair)
        for key,val in response.items():
            symbol = key.replace("_","")
            for item in val:
                id = item["orderNumber"]
                price = float(item["rate"])
                amount = float(item["amount"])
                type = item["type"]
                orders.append({"symbol":symbol,"id":id,"price":price,"amount":amount,"type":type})
        return orders

    def get_deposit_address(self,asset):
        """Returns all of your deposit addresses."""
        asset = asset.upper()
        addresses = self._private('returnDepositAddresses')
        if asset in addresses.keys():
            address = addresses[asset]
        else:
            print("creating new")
            address = self._private('generateNewAddress', currency=asset)["response"]  # create and return new address
        return {"asset":asset,"address":address}

    def withdraw(self, currency, amount, address, paymentId=None):
        """Immediately places a withdrawal for a given currency, with no email
        confirmation. In order to use this method, the withdrawal privilege
        must be enabled for your API key. Required POST parameters are
        "currency", "amount", and "address". For XMR withdrawals, you may
        optionally specify "paymentId"."""
        return self._private('withdraw', currency=currency, amount=amount,
                             address=address, paymentId=paymentId)

    def get_trade_history(self, base, quote, limit=500):
        """Returns your trade history for a given market, specified by the
        "currencyPair" POST parameter. You may specify "all" as the
        currencyPair to receive your trade history for all markets. You may
        optionally specify a range via "start" and/or "end" POST parameters,
        given in UNIX timestamp format; if you do not specify a range, it will
        be limited to one day."""
        start = 0
        end = int(_time.time())
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
        end = int(_time.time())
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
        end = int(_time.time())
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

    def get_trade_fee(self,base,quote):
        """If you are enrolled in the maker-taker fee schedule, returns your
        current trading fees and trailing 30-day volume in BTC. This
        information is updated once every 24 hours."""
        response = self._private('returnFeeInfo')
        maker_fee = float(response["makerFee"]) # returns value in BTC
        taker_fee = float(response["takerFee"]) # returns value in BTC
        return {"exchange":"poloniex","maker_fee":maker_fee,"taker_fee":taker_fee}

    def get_withdraw_fee(self,asset):
        response = self._public('returnCurrencies')
        try:
            fee =float(response[asset.upper()]["txFee"])
            return {"asset":asset.upper(),"withdraw_fee":fee}
        except:
            return None



    def transferBalance(self, currency, amount, fromAccount, toAccount):
        """Transfers funds from one account to another (e.g. from your exchange
         account to your margin account). Required POST parameters are
         "currency", "amount", "fromAccount", and "toAccount"."""
        return self._private('transferBalance', currency=currency,amount=amount, fromAccount=fromAccount,toAccount=toAccount)


#-------------------
# Streaming Classes
#-------------------

class PoloniexWebsocket(WebSocket):

    url = "wss://api2.poloniex.com:443"

    currency_codes = {"7":"BTC_BCN","8":"BTC_BELA","10":"BTC_BLK","12":"BTC_BTCD","13":"BTC_BTM","14":"BTC_BTS",
                      "15":"BTC_BURST","20":"BTC_CLAM","24":"BTC_DASH","25":"BTC_DGB","27":"BTC_DOGE","28":"BTC_EMC2",
                      "31":"BTC_FLDC","32":"BTC_FLO","38":"BTC_GAME","40":"BTC_GRC","43":"BTC_HUC","50":"BTC_LTC",
                      "51":"BTC_MAID","58":"BTC_OMNI","61":"BTC_NAV","63":"BTC_NEOS","64":"BTC_NMC","69":"BTC_NXT",
                      "73":"BTC_PINK","74":"BTC_POT","75":"BTC_PPC","83":"BTC_RIC","89":"BTC_STR","92":"BTC_SYS",
                      "97":"BTC_VIA","98":"BTC_XVC","99":"BTC_VRC","100":"BTC_VTC","104":"BTC_XBC","108":"BTC_XCP",
                      "112":"BTC_XEM","114":"BTC_XMR","116":"BTC_XPM","117":"BTC_XRP","121":"USDT_BTC","122":"USDT_DASH",
                      "123":"USDT_LTC","124":"USDT_NXT","125":"USDT_STR","126":"USDT_XMR","127":"USDT_XRP","129":"XMR_BCN",
                      "130":"XMR_BLK","131":"XMR_BTCD","132":"XMR_DASH","137":"XMR_LTC","138":"XMR_MAID","140":"XMR_NXT",
                      "148":"BTC_ETH","149":"USDT_ETH","150":"BTC_SC","151":"BTC_BCY","153":"BTC_EXP","155":"BTC_FCT",
                      "158":"BTC_RADS","160":"BTC_AMP","162":"BTC_DCR","163":"BTC_LSK","166":"ETH_LSK","167":"BTC_LBC",
                      "168":"BTC_STEEM","169":"ETH_STEEM","170":"BTC_SBD","171":"BTC_ETC","172":"ETH_ETC","173":"USDT_ETC",
                      "174":"BTC_REP","175":"USDT_REP","176":"ETH_REP","177":"BTC_ARDR","178":"BTC_ZEC","179":"ETH_ZEC",
                      "180":"USDT_ZEC","181":"XMR_ZEC","182":"BTC_STRAT","183":"BTC_NXC","184":"BTC_PASC","185":"BTC_GNT",
                      "186":"ETH_GNT","187":"BTC_GNO","188":"ETH_GNO","189":"BTC_BCH","190":"ETH_BCH","191":"USDT_BCH",
                      "192":"BTC_ZRX","193":"ETH_ZRX","194":"BTC_CVC","195":"ETH_CVC","196":"BTC_OMG","197":"ETH_OMG",
                      "198":"BTC_GAS","199":"ETH_GAS","200":"BTC_STORJ","201":"BTC_EOS","202":"ETH_EOS","203":"USDT_EOS"}


    def __init__(self,symbols):
        self.symbols = symbols
        self.socket = self.connect()
        self.subscribe(1002)

    def subscribe(self,channel,command="subscribe"):
        # Can only subscribe to one channel per socket in think
        """1010:	Heartbeat
           1002:	Ticker
           1003:	24 hour Exchange Volume"""

        data = {"command" : command, "channel" : channel}
        self.socket.send(dumps(data))

    def start(self):
        while True:
            result = self.socket.recv()
            try:
                result = loads(result)
                if len(result) > 2:
                    t = Thread(target=self.process_response,args=[result])
                    t.daemon = True
                    t.start()
            except json.decoder.JSONDecodeError: # This means nothing was received for json to decode
                self.reconnect()
                self.subscribe(1002)

    def process_ticker(self,msg):
        if result[2][0] in self.symbols:
            price = result[2][1] # save to database here

    def convert_to_symbol(self,code):
        """ return symbol from symbol code """
        pass

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
