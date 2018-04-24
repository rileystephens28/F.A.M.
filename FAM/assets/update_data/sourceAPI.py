import abc

class SourceAPI:

    """docstring for SourceAPI"""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_tradeable_assets(self):
        """ returns all tradeable assets from the specified source """
        return NotImplemented

    @abc.abstractmethod
    def get_ticker(self, symbol):
        """ returns ticker data for a given symbol """
        return NotImplemented

    @abc.abstractmethod
    def get_all_tickers(self):
        """ returns ticker data for all symbols from given source """
        return NotImplemented

    @abc.abstractmethod
    def get_candlestick(self,symbol,days):
        """ return candlestick data for a given symbol for a specified amount of time """
        return NotImplemented
