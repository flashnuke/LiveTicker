import requests
import websockets
import json
import asyncio
import os
import certifi


class Binance:
    def __init__(self):
        self._BASE_REST = "https://api.binance.com"
        self._BASE_WS = "wss://stream.binance.com:9443"

        self.tickers = dict()
        self.tickers = {symbol['symbol'].upper(): 0 for symbol in self.get_symbols_rest()}

    async def stream_manager(self, symbol: str, cb_func):
        """
        manage the stream
        """
        full_path = self._BASE_WS + f"/stream?streams={symbol.lower()}@aggTrade"
        os.environ['SSL_CERT_FILE'] = certifi.where()  # set ssl certificate

        async with websockets.connect(full_path) as ws:
            while True:
                try:
                    result = await ws.recv()
                    result = json.loads(result)
                    self.trade_stream_parser(result['data'])
                    cb_func(self.tickers[symbol.upper()])

                except ConnectionAbortedError:
                    print(f"Exception '{ConnectionAbortedError.__name__}' in re-establishing ws")

                except Exception as wsexc:
                    print(f"Exception {wsexc} in websocket")

    def start_stream(self, symbol: str, cb_func):
        """
        start a websocket stream and pass the price into the callback function
        a loop is used in which an event loop is created each time it disconnects
        """
        # self.tickers[symbol.upper()] = float()  # will be used to store latest price of ticker

        while True:  # loop in case disconnects
            asyncio.new_event_loop().run_until_complete(self.stream_manager(symbol, cb_func))

    def trade_stream_parser(self, msg: dict):
        """
        callback for stream to parse trades msgs
        """
        ticker_name, last_price = msg['s'], msg['p']

        self.tickers[ticker_name] = float(last_price)

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
        return self.get_price_rest(symbol) if use_rest else self.tickers[symbol.upper()]

    def get_tickers(self):
        """
        getter for self.tickers
        """
        return self.tickers
