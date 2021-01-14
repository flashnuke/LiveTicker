import requests
import websockets
import json
import asyncio
import os
import certifi
from math import log10


class Binance:
    """
    _BASE_REST - base for REST path
    _BASE_WS - base for WS path

    tickers - a dict containing all symbols and their prices (if connected)
    _ticker_precision - quote precision for all tickers
    _connected_tickers - all currenctly connected tickers
    """

    def __init__(self):
        self._BASE_REST = "https://api.binance.com"
        self._BASE_WS = "wss://stream.binance.com:9443"

        self._tickers = dict()
        self._ticker_precision = dict()
        self._connected_tickers = set()

        self.set_up_tickers()

    @staticmethod
    def get_precision_based_on_ticksize(ticksize: float):
        """
        returns precision based on ticksize
        # todo: lru_cache
        """
        return int(-log10(ticksize)) if ticksize < 1 else 0

    def set_up_tickers(self):
        """
        sets up all tickers and their precision
        """
        all_symbols = self.get_symbols_rest()
        for symbol in all_symbols:
            if symbol['status'] == "TRADING":
                self._tickers[symbol['symbol']] = float()
                for s_filter in symbol['filters']:
                    if s_filter['filterType'] == 'PRICE_FILTER':
                        self._ticker_precision[symbol['symbol']] = \
                            self.get_precision_based_on_ticksize(float(s_filter['tickSize']))

    def get_precision(self, symbol: str):
        """
        get precision based on symbol
        """
        return self._ticker_precision[symbol]

    async def stream_manager(self, symbol: str, cb_func):
        """
        manage the stream
        """
        full_path = self._BASE_WS + f"/stream?streams={symbol.lower()}@aggTrade"
        os.environ['SSL_CERT_FILE'] = certifi.where()  # set ssl certificate

        async with websockets.connect(full_path) as ws:
            while symbol.upper() in self._connected_tickers:
                try:
                    result = await ws.recv()
                    result = json.loads(result)
                    self.trade_stream_parser(result['data'])
                    cb_func(self._tickers[symbol.upper()])

                except ConnectionAbortedError:
                    print(f"Exception '{ConnectionAbortedError.__name__}' in re-establishing ws")

                except Exception as wsexc:
                    print(f"Exception {wsexc} in websocket")

    def _connect_ticker(self, symbol: str):
        """
        add ticker to `self._connected_tickers` set
        """
        self._connected_tickers.add(symbol.upper())

    def _disconnect_ticker(self, symbol: str):
        """
        remove ticker from `self._connected_tickers` set
        """
        self._connected_tickers.remove(symbol.upper())

    def end_stream(self, symbol):
        """
        method used to end stream
        """
        self._disconnect_ticker(symbol)

    def start_stream(self, symbol: str, cb_func):
        """
        start a websocket stream and pass the price into the callback function
        a loop is used in which an event loop is created each time it disconnects

        `self.connected_tickers` is used to keep track of connected tickers and maintain the abiltiy to disconnect
        """
        self._connect_ticker(symbol)

        while symbol.upper() in self._connected_tickers:  # loop in case disconnects
            asyncio.new_event_loop().run_until_complete(self.stream_manager(symbol, cb_func))

    def trade_stream_parser(self, msg: dict):
        """
        callback for stream to parse trades msgs
        """
        ticker_name, last_price = msg['s'], msg['p']

        self._tickers[ticker_name] = float(last_price)

    def get_price_rest(self, symbol: str):
        """
        Fetches price using REST
        """
        return float(requests.get(self._BASE_REST + f"/api/v3/avgPrice?symbol={symbol.upper()}").json()["price"])

    def get_symbols_rest(self):
        """
        Fetches symbols using REST
        used to initialzie a dict containing last prices for all symbols
        ws_stream uses this dict to update entries
        """
        response = requests.get(self._BASE_REST + "/api/v3/exchangeInfo").json()['symbols']
        return response

    def get_price(self, symbol: str, use_rest: bool):
        """
        if use_rest is  true, using REST to fetch price. else: handle locally by WS
        """
        return self.get_price_rest(symbol) if use_rest else self._tickers[symbol.upper()]

    def get_tickers(self):
        """
        getter for self.tickers
        """
        return self._tickers
