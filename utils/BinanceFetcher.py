import requests
import websocket
import json


class Binance:
    def __init__(self):
        self._BASE_REST = "https://api.binance.com"
        self._BASE_WS = "wss://stream.binance.com:9443"

        self.tickers = dict()

    def start_stream(self, symbol: str, cb_func):
        """
        start a websocket stream and pass the price into the callback function
        """
        self.tickers[symbol.upper()] = float()  # will be used to store latest price of ticker
        full_path = self._BASE_WS + f"/stream?streams={symbol.lower()}@aggTrade"

        ws = websocket.create_connection(full_path)

        while True:
            try:
                result = ws.recv()
                result = json.loads(result)
                self.trade_stream_parser(result['data'])
                cb_func(self.tickers[symbol.upper()])

            except websocket.WebSocketConnectionClosedException:
                try:
                    ws = websocket.create_connection(full_path)
                except Exception as establishexc:
                    print(f"Exception '{establishexc}' in re-establishing ws")

            except ConnectionAbortedError:
                try:
                    ws = websocket.create_connection(full_path)
                except Exception as establishexc:
                    print(f"Exception '{establishexc}' in re-establishing ws")

            except Exception as wsexc:
                ws = websocket.create_connection(full_path)
                print(f"Exception {wsexc} in websocket")

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

    def get_price(self, symbol: str, use_rest: bool):
        """
        if use_rest is  true, using REST to fetch price. else: handle locally by WS
        """
        return self.get_price_rest(symbol) if use_rest else self.tickers[symbol.upper()]

