import abc

class MarketAPI:

    """docstring for MarketAPI"""

    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        super(MarketAPI, self).__init__()
        self.name = name
        self.available_assets = self.get_available_assets()

    # Output:
    @abc.abstractmethod
    def get_available_assets(self):
        return NotImplemented

    @abc.abstractmethod
    def get_ticker(self, asset):
        '''
        returns all bids (someone wants to buy Base from you)
        and asks (someone offering to sell base to you).
        If exchange does not support the base_alt market but supports
        the alt_base market instead, it is up to the exchange to convert
        retrieved data to the desired format.
        '''
        return NotImplemented

    def get_multiple_tickers(self, list):
        """
        returns entire orderbook for multiple exchanges.
        Very useful for triangular arb, but note that not all exchanges support this.
        the default implementation is to simply fetch one pair at a time, but this is very slow.
        Some exchanges already provide full orderbooks when fetching market data, so superclass those.
        """
        return NotImplemented
