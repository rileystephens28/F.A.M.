import abc

class SourceAPI:

    """docstring for SourceAPI"""

    __metaclass__ = abc.ABCMeta


    def __init__(self, name):
        super(SourceAPI, self).__init__()
        self.name = name

    # Output:
    @abc.abstractmethod
    def get_tradeable_assets(self):
        return NotImplemented

    @abc.abstractmethod
    def get_data(self, base, alt):
        '''
        returns all bids (someone wants to buy Base from you)
        and asks (someone offering to sell base to you).
        If exchange does not support the base_alt market but supports
        the alt_base market instead, it is up to the exchange to convert
        retrieved data to the desired format.
        '''
        return NotImplemented

    @abc.abstractmethod
    def get_all_data(self):
        """
        returns entire orderbook for multiple exchanges.
        Very useful for triangular arb, but note that not all exchanges support this.
        the default implementation is to simply fetch one pair at a time, but this is very slow.
        Some exchanges already provide full orderbooks when fetching market data, so superclass those.
        """
        return NotImplemented

    def stream_data(self):
        """
        opens up client socket for each currency pair and begins continuously streaming ticker
        data to cryptocurrency get_tradeable_pairs.
        """
        return NotImplemented
