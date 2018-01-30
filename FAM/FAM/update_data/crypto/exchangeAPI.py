import abc

class ExchangeAPI:

    """docstring for ExchangeAPI"""

    __metaclass__ = abc.ABCMeta


    def __init__(self, name):
        super(ExchangeAPI, self).__init__()
        self.name = name
        self.tradeable_pairs = self.get_tradeable_pairs()

    # Output:
    @abc.abstractmethod
    def get_tradeable_pairs(self):
        return NotImplemented

    @abc.abstractmethod
    def get_depth(self, base, alt):
        '''
        returns all bids (someone wants to buy Base from you)
        and asks (someone offering to sell base to you).
        If exchange does not support the base_alt market but supports
        the alt_base market instead, it is up to the exchange to convert
        retrieved data to the desired format.
        '''
        return NotImplemented

    @abc.abstractmethod
    def get_multiple_depths(self, pairs):
        """
        returns entire orderbook for multiple exchanges.
        Very useful for triangular arb, but note that not all exchanges support this.
        the default implementation is to simply fetch one pair at a time, but this is very slow.
        Some exchanges already provide full orderbooks when fetching market data, so superclass those.
        """
        return NotImplemented
