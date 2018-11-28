import json
import requests
import inspect
import six
import time
from datetime import datetime
from threading import Thread
from urllib.parse import quote
from urllib.parse import urlparse
from websocket import create_connection
from django.db import connection, connections
from exchanges.models import Exchange
from currencies.models import Currency, CurrencyPair
from exchanges.apis.websocket_utils import WebSocket, StreamingError

imap = map

class HitbtcClient:
    """ API Client for the HitBTC REST API.
        Full API docs, including descriptions of each API and its parameters, are available here: https://api.hitbtc.com/"""

    BASE_API_URI = 'https://api.hitbtc.com/api/2/' #latest v2

    def __init__(self,api_key,secret_key,base_api_uri=None):
        self._key = api_key
        self._secret = secret_key
        self.get_session()

    def get_session(self):
        """
        Internal helper for creating a requests `session` with the correct authentication handling.
        """
        self._session = requests.session()
        self._session.auth = (self._key, self._secret)

    def _create_api_uri(self,*dirs):
        """
        Internal helper for creating fully qualified endpoint URIs.
        """
        return self.BASE_API_URI +'/'.join(imap(quote,dirs))

    def _request(self,method,*dirs,**kwargs):
        """
        Internal helper for creating HTTP requests to the HitBTC API. Returns the HTTP response.
        """
        uri = self._create_api_uri(*dirs)
        return getattr(self._session,method)(uri,**kwargs)

    def _handle_response(self,response):
        """
        Internal helper for handling API responses from the HitBTC server. Raises the appropriate exceptions when response is not 200; otherwise, returns the response.
        """
        if response.status_code != 200:
            raise api_response_error(response)
        return response.json()

    def _get(self,*dirs,**kwargs):
        return self._request('get',*dirs,**kwargs)

    def _check_req_params(self,req_params,params):
        """
        Internal helper to check if all required parameters for the method have been provided. Raises ParameterRequiredError if any of the required parameters is missing.
        """
        if not all(req_p in params for req_p in req_params):
            raise ParameterRequiredError('Missing required parameter(s) %s' % req_params)

# -----------------------
#  Start Manager Methods
# -----------------------

    def get_currencies(self,**params):
        currencies = []
        response = self._get('public','currency',params=params)
        products = self._handle_response(response)
        for product in products:
            currencies.append(product["id"].upper())
        return list(set(currencies))

    def get_currency_pairs(self,**params):
        currency_pairs = []
        response = self._get('public','symbol',params=params)
        products = self._handle_response(response)
        for product in products:
            base = product["baseCurrency"]
            quote = product["quoteCurrency"]
            currency_pair = base + quote
            currency_pairs.append({"currency_pair":currency_pair,"base":base,"quote":quote})
        return currency_pairs


    def get_balances(self,**params):
        balances = []
        response = self._get('account','balance',params=params)
        response = self._handle_response(response)
        for balance in response:
            asset = balance["currency"]
            tradable = float(balance["available"])
            locked = float(balance["reserved"])
            balances.append({"asset":asset,"tradable":tradable,"locked":locked})
        return balances

    def get_trade_history(self,base,quote,**params):
        orders = []
        symbol = base.upper() + quote.upper()
        params.update({"symbol":symbol})
        response = self._get('history','trades',params=params)
        response = self._handle_response(response)
        for order in response:
            symbol = order["symbol"]
            id = order["clientOrderId"]
            price = float(order["price"])
            amount = float(order["quantity"])
            time = datetime.strptime(order["timestamp"],"%Y-%m-%dT%H:%M:%S.%fZ")
            type = order["side"]
            orders.append({"symbol":symbol,"id":id,"time":time,"price":price,"amount":amount,"type":type})
        return orders

    def get_deposit_history(self,asset,**params):
        deposits = []
        response = self._get('account','transactions',params=params)
        response = self._handle_response(response)
        deposit_list = list([item for item in response if item["type"]=="payin"])
        for deposit in deposit_list:
            if deposit["currency"] == asset.upper():
                asset = deposit["currency"]
                time = datetime.strptime(deposit["createdAt"],"%Y-%m-%dT%H:%M:%S.%fZ")
                amount = deposit["amount"]
                address = "NA"
                status = "Complete" if deposit["status"] == "success" else "Pending"
                deposits.append({"asset":asset,"time":time,"amount":amount,"address":address,"status":status})
        return deposits

    def get_withdraw_history(self,asset,**params):
        withdraws = []
        response = self._get('account','transactions',params=params)
        response = self._handle_response(response)
        withdraw_list = list([item for item in response if item["type"]=="payout"])
        for withdraw in withdraw_list:
            #print(withdraw)
            if withdraw["currency"] == asset.upper():
                asset = withdraw["currency"]
                time = datetime.strptime(withdraw["createdAt"],"%Y-%m-%dT%H:%M:%S.%fZ")
                amount = withdraw["amount"]
                address = withdraw["address"]
                status = "Complete" if withdraw["status"] == "success" else "Pending"
                withdraws.append({"asset":asset,"time":time,"amount":amount,"address":address,"status":status})
        return withdraws

# -----------------------
#  End Manager Methods
# -----------------------

#-------------------
# Streaming Classes
#-------------------

class HitbtcWebsocket(WebSocket):

    url = "wss://api.hitbtc.com/api/2/ws"

    def __init__(self,symbols):
        self.symbols = symbols
        self.exchange = Exchange.objects.get(name="HitBTC")
        super().__init__()
        self.subscribe()

    def subscribe(self):
        for symbol in self.symbols:
            data = { "method": "subscribeTicker", "params": { "symbol": symbol.upper() }, "id": symbol.upper() }
            self.socket.send(json.dumps(data))

    def start(self):
        while True:
            result = self.socket.recv()
            try:
                result = json.loads(result)
                if 'params' in result.keys():
                    t = Thread(target=self.process_ticker,args=[result])
                    t.daemon = True
                    t.start()
            except json.decoder.JSONDecodeError: # This means nothing was received for json to decode
                StreamingError()
                self.reconnect()
            time.sleep(.3)

    def process_ticker(self,msg):
        bid = float("%.2f"%float(msg['params']['bid']))
        ask = float("%.2f"%float(msg['params']['ask']))
        last = float("%.2f"%float(msg['params']['last']))
        base_volume = float("%.2f"%float(msg['params']['volume']))
        quote_volume = float("%.2f"%float(msg['params']['volumeQuote']))
        CurrencyPair.objects.filter(symbol=msg['params']['symbol'],base__exchange=self.exchange).update(bid=bid,ask=ask,last=last,base_volume=base_volume,quote_volume=quote_volume)
        connection.close()
        print("hitbtc  ", msg['params']['symbol'], last)



class HitBTCError(Exception):
    """
    Base error class for all exceptions raised in this library.
    Will never be raised naked; more specific subclasses of this exception will be raised when appropriate.
    """

class ParameterRequiredError(HitBTCError): pass

# response error handling
class APIError(HitBTCError):
    """
    Raised for errors related to interaction with the HitBTC API server.
    """
    def __init__(self,status_code,error_msg,error_desc):
        self.status_code = status_code
        self.error_msg = error_msg or ''
        self.error_desc = error_desc or ''
        if self.error_desc:
            self.error_desc = '(%s)' % self.error_desc

    def __str__(self):
        return '%s %s %s' % (self.status_code,self.error_msg,self.error_desc)



class InvalidRequestError(APIError): pass
class AuthenticationError(APIError): pass
class TwoFactorRequiredError(APIError): pass
class InvalidScopeError(APIError): pass
class NotFoundError(APIError): pass
class ValidationError(APIError): pass
class RateLimitExceededError(APIError): pass
class InternalServerError(APIError): pass
class ServiceUnavailableError(APIError): pass
class GatewayTimeoutError(APIError): pass

def api_response_error(response):
    """
    Helper method for creating errors and attaching HTTP response details to them.
    """
    error_msg = str(response.reason) or ''
    error_desc = ''
    if 'json' in response.headers.get('content-type'):
        error = response.json().get('error',None)
        if error:
            error_msg = error.get('message',None)
            error_desc = error.get('description',None)

    error_class = _status_code_to_class.get(response.status_code,APIError)
    return error_class(response.status_code,error_msg,error_desc)



_status_code_to_class = {
    400: InvalidRequestError,
    401: AuthenticationError,
    402: TwoFactorRequiredError,
    403: InvalidScopeError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitExceededError,
    500: InternalServerError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
  }
