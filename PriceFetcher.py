from utils import BinanceFetcher as BinanceFetcher

class Fetcher:
    """
    A higher class used for implementing price fetching methods.
    """
    exchange_mapper = dict()
    exchange_mapper['Binance'] = BinanceFetcher

    def __init__(self, ex_name: str):
        if ex_name in self.exchange_mapper:
            self.exchange_manager = self.exchange_mapper['ex_name']
        else:
            raise Exception(f"Exchange {ex_name} is not supported")

    def fetch_price(self, symbol: str):
        """
        if connected ws, will simply return price.
        else: use REST
        """
        return self.exchange_manager.get_price(symbol)

    def connect_ws(self, symbol: str):
        self.exchange_manager.start_stream(symbol)
