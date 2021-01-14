from utils.BinanceFetcher import Binance
from functools import lru_cache


class Fetcher:
    """
    A higher class used for implementing price fetching methods.
    """
    exchange_mapper = dict()
    exchange_mapper['Binance'] = Binance

    def __init__(self, ex_name: str):
        if ex_name in self.exchange_mapper:
            self.exchange_manager = self.exchange_mapper[ex_name]()
        else:
            raise Exception(f"Exchange {ex_name} is not supported")

    def fetch_price(self, symbol: str, use_rest: bool):
        """
        if connected ws, will simply return price.
        else: use REST
        """
        return self.exchange_manager.get_price(symbol, use_rest)

    def connect_ws(self, symbol: str, cb_func):
        """
        connect to ws stream and pass a callback function
        """
        self.exchange_manager.start_stream(symbol, cb_func)

    def disconnect_ws(self, symbol: str):
        """
        disconnect ticker ws stream
        """
        self.exchange_manager.end_stream(symbol)

    def get_all_symbols(self):
        """
        get all possible tickers for a certain exchange
        """
        return self.exchange_manager.get_tickers()

    @lru_cache()
    def get_symbol_precision(self, symbol: str):
        """
        returns symbol precision for proper printing
        # todo: lru_cache()
        """
        return self.exchange_manager.get_precision(symbol)
