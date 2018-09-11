import hashlib
import hmac
import requests
import six
import time
import sys
from threading import Thread
from datetime import datetime, timedelta, date
from exchanges.API.websocket_utils import WebSocket, StreamingError
import json
from urllib.parse import urlencode

class BinanceClient:

    API_URL = 'https://api.binance.com/api'
    WITHDRAW_API_URL = 'https://api.binance.com/wapi'
    WEBSITE_URL = 'https://www.binance.com'
    PUBLIC_API_VERSION = 'v1'
    PRIVATE_API_VERSION = 'v3'
    WITHDRAW_API_VERSION = 'v3'

    KLINE_INTERVAL_1MINUTE = '1m'
    KLINE_INTERVAL_3MINUTE = '3m'
    KLINE_INTERVAL_5MINUTE = '5m'
    KLINE_INTERVAL_15MINUTE = '15m'
    KLINE_INTERVAL_30MINUTE = '30m'
    KLINE_INTERVAL_1HOUR = '1h'
    KLINE_INTERVAL_2HOUR = '2h'
    KLINE_INTERVAL_4HOUR = '4h'
    KLINE_INTERVAL_6HOUR = '6h'
    KLINE_INTERVAL_8HOUR = '8h'
    KLINE_INTERVAL_12HOUR = '12h'
    KLINE_INTERVAL_1DAY = '1d'
    KLINE_INTERVAL_3DAY = '3d'
    KLINE_INTERVAL_1WEEK = '1w'
    KLINE_INTERVAL_1MONTH = '1M'

    def __init__(self,api_key,secret_key):
        """
        param api_key: Api Key --> type = str
        param api_secret: Api Secret --> type = str.
        """

        self.API_KEY = api_key
        self.API_SECRET = secret_key
        self.session = self.get_session()
        self.ping()# init DNS and SSL cert

    def get_session(self):
        session = requests.session()
        session.headers.update({'Accept': 'application/json','User-Agent': 'binance/python','X-MBX-APIKEY': self.API_KEY})
        return session

    def get_uri(self, path, signed=True, version=PUBLIC_API_VERSION):
        if signed:
            v = self.PRIVATE_API_VERSION
        else:
            v = version
        return self.API_URL + '/' + v + '/' + path

    def _create_withdraw_api_uri(self, path):
        return self.WITHDRAW_API_URL + '/' + self.WITHDRAW_API_VERSION + '/' + path

    def get_website_uri(self, path):
        return self.WEBSITE_URL + '/' + path

    def get_signature(self, data):
        query_string = urlencode(data)
        m = hmac.new(self.API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
        return m.hexdigest()

    def get_order_params(self, data):
        """Convert params to list with signature as last element"""
        has_signature = False
        params = []
        for key, value in data.items():
            if key == 'signature':
                has_signature = True
            else:
                params.append((key, value))
        if has_signature:
            params.append(('signature', data['signature']))
        return params

    def _request(self, method, uri, signed, time_adjust=0, force_params=False, **kwargs):
        retry_attemps = 0
        while retry_attemps < 20:
            data = kwargs.get('data', None)
            if data and isinstance(data, dict):
                kwargs['data'] = data
            if signed:
                # generate signature
                kwargs['data']['timestamp'] = int(time.time()*1000+time_adjust)
                kwargs['data']['signature'] = self.get_signature(kwargs['data'])
            if data and (method == 'get' or force_params):
                kwargs['params'] = self.get_order_params(kwargs['data'])
                temp_data = kwargs['data']
                del(temp_data["timestamp"])
                del(temp_data["signature"])
                del(kwargs['data'])
            response = getattr(self.session, method)(uri, **kwargs)
            msg = self._handle_response(response)
            msg_str = None
            if type(msg) is dict:
                if "success" in msg.keys():
                    if msg["success"]:
                        return msg
                    else:
                        msg_str = json.loads(msg["msg"])["msg"]
                elif "msg" in msg.keys():
                    msg_str = msg["msg"]
                if msg_str:
                    if "1000ms ahead" in msg_str:
                        print("I'm ahead, adjusting request time")
                        time_adjust -= 1000
                        kwargs = {'data': temp_data}
                    elif "Timestamp for this request is outside of the recvWindow" in msg_str:
                        print("I'm behind, adjusting request time")
                        time_adjust += 1000
                        kwargs = {'data': temp_data}
                else:
                    return msg
            else:
                return msg
            retry_attemps += 1
            time.sleep(.5)
        print("Retry attempts exceeded. Quiting program...")
        sys.exit()

    def _request_api(self, method, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        uri = self.get_uri(path, signed, version)
        return self._request(method, uri, signed, **kwargs)

    def _request_withdraw_api(self, method, path, signed=False, **kwargs):
        uri = self._create_withdraw_api_uri(path)
        return self._request(method, uri, signed, force_params=True, **kwargs)

    def _request_website(self, method, path, signed=False, **kwargs):
        uri = self.get_website_uri(path)
        return self._request(method, uri, signed, **kwargs)

    def _handle_response(self, response):
        """Internal helper for handling API responses from the Binance server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status_code).startswith('2'):
            if not str(response.status_code).startswith('4'):
                raise BinanceAPIException(response)
        try:
             return response.json()
        except ValueError:
            raise BinanceRequestException('Invalid Response: %s' % response.text)
        except:
            print(response.text)

    def _get(self, path, signed=False, version=PUBLIC_API_VERSION, **kwargs):
        return self._request_api('get', path, signed, version, **kwargs)

    # General Endpoints

    def ping(self):
        """Test connectivity to the Rest API."""
        return self._get('ping')

    def get_server_time(self):
        """Test connectivity to the Rest API and get the current server time."""
        return self._get('time')


# -----------------------
#  End Manager Methods
# -----------------------

    def get_currencies(self):
        """Return list of products currently listed on Binance"""
        currencies = []
        products = self._request_website('get', 'exchange/public/product')
        for currency in products["data"]:
            currencies.append(currency["baseAsset"].upper())
            currencies.append(currency["quoteAsset"].upper())
        return list(set(currencies))

    def get_currency_pairs(self):
        """Return list of products currently listed on Binance"""
        currency_pairs = []
        products = self._request_website('get', 'exchange/public/product')
        for product in products["data"]:
            base = product["baseAsset"].upper()
            quote = product["quoteAsset"].upper()
            currency_pair = base + quote
            currency_pairs.append({"currency_pair":currency_pair,"base":base,"quote":quote})
        return currency_pairs

    def get_balances(self, **params):
        """Get current asset balance."""
        response = self._get('account', True, data=params)
        # find asset balance in list of balances
        balances = []
        if "balances" in response:
            for balance in response['balances']:
                asset = balance["asset"]
                tradable = balance["free"]
                locked = balance["locked"]
                balances.append({"asset":asset,"tradable":tradable,"locked":locked})
            return balances
        return None

    def get_trade_history(self, base, quote,**params):
        """Get trades for a specific symbol."""
        orders = []
        symbol = base + quote
        params.update({"symbol":symbol})
        response = self._get('myTrades', True, data=params)
        for order in response:
            symbol = order["symbol"]
            id = order["orderId"]
            price = float(order["price"])
            amount = float(order["qty"])
            time = datetime.fromtimestamp(int(order["time"])/1000)
            if order["isBuyer"]:
                type = "buy"
            else:
                type = "sell"
            orders.append({"symbol":symbol,"id":id,"time":time,"price":price,"amount":amount,"type":type})
        return orders

    def get_deposit_history(self,asset,**params):
        """Fetch deposit history."""
        deposits = []
        params.update({"asset":asset.upper()})
        response = self._request_withdraw_api('get', 'depositHistory.html', True, data=params)
        for deposit in response["depositList"]:
            asset = deposit["asset"]
            time = datetime.fromtimestamp(int(deposit["insertTime"])/1000)
            amount = deposit["amount"]
            address = deposit["address"]
            status = "Complete" if deposit["status"] == 1 else "Pending"
            deposits.append({"asset":asset,"time":time,"amount":amount,"address":address,"status":status})
        return deposits


    def get_withdraw_history(self,asset,**params):
        """Fetch withdraw history."""
        withdraws = []
        params.update({"asset":asset.upper()})
        response = self._request_withdraw_api('get', 'withdrawHistory.html', True, data=params)
        for withdraw in response["withdrawList"]:
            asset = withdraw["asset"]
            time = datetime.fromtimestamp(int(withdraw["applyTime"])/1000)
            amount = withdraw["amount"]
            address = withdraw["address"]
            if withdraw["status"] == 1:
                status = "Canceled"
            elif withdraw["status"] == 2:
                status = "Awaiting Approval"
            elif withdraw["status"] == 3:
                status = "Rejected"
            elif withdraw["status"] == 4:
                status = "Processing"
            elif withdraw["status"] == 5:
                status = "Failure"
            elif withdraw["status"] == 6:
                status = "Completed"
            withdraws.append({"asset":asset,"time":time,"amount":amount,"address":address,"status":status})
        return withdraws

# -----------------------
#  End Manager Methods
# -----------------------

#-------------------
# Streaming Classes
#-------------------

class BinanceWebsocket(WebSocket):

    def __init__(self):
        symbols = list([item.lower()+"@ticker" for item in symbols])
        symbols = ",".join(symbols)
        self.url = 'wss://stream.binance.com:9443/ws/'+symbols
        self.symbols = symbols
        super().__init__()

    def start(self):
        while True:
            result = self.socket.recv()
            try:
                result = json.loads(result)
                if len(result) > 2:
                    t = Thread(target=self.process_ticker,args=[result])
                    t.daemon = True
                    t.start()
            except json.decoder.JSONDecodeError: # This means nothing was received for json to decode
                StreamingError(str(datetime.now())+" --> Binance streaming error occured. Reconnecting now.")
                self.reconnect()

    def process_ticker(self,msg):
        print(msg['c'])


#-------------------
# Exception Classes
#-------------------

class BinanceAPIException(Exception):

    LISTENKEY_NOT_EXIST = '-1125'

    def __init__(self, response):
        json_res = response.json()
        self.status_code = response.status_code
        self.response = response
        self.code = json_res['code']
        self.message = json_res['msg']
        self.request = getattr(response, 'request', None)

    def notify(self):
        if self.message == "Invalid API-key, IP, or permissions for action.":
            return True
        if "time" in self.message:
            return False

    def __str__(self):  # pragma: no cover
        return 'APIError(code=%s): %s' % (self.code, self.message)

class BinanceRequestException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return 'BinanceRequestException: %s' % self.message


class BinanceOrderException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'BinanceOrderException(code=%s): %s' % (self.code, self.message)


class BinanceOrderMinAmountException(BinanceOrderException):

    def __init__(self, value):
        message = "Amount must be a multiple of %s" % value
        super(BinanceOrderMinAmountException, self).__init__(-1013, message)


class BinanceOrderMinPriceException(BinanceOrderException):

    def __init__(self, value):
        message = "Price must be at least %s" % value
        super(BinanceOrderMinPriceException, self).__init__(-1013, message)


class BinanceOrderMinTotalException(BinanceOrderException):

    def __init__(self, value):
        message = "Total must be at least %s" % value
        super(BinanceOrderMinTotalException, self).__init__(-1013, message)


class BinanceOrderUnknownSymbolException(BinanceOrderException):

    def __init__(self, value):
        message = "Unknown symbol %s" % value
        super(BinanceOrderUnknownSymbolException, self).__init__(-1013, message)


class BinanceOrderInactiveSymbolException(BinanceOrderException):

    def __init__(self, value):
        message = "Attempting to trade an inactive symbol %s" % value
        super(BinanceOrderInactiveSymbolException, self).__init__(-1013, message)

# sock = BinanceWebsocket(["ETHBTC"])
# sock.start()
