import asyncio
import aiohttp


class Binance:
    def __init__(self):
        self._BASE_REST = "https://api.binance.com"
        self._BASE_WS = "wss://stream.binance.com:9443"

        self.tickers = dict()

    async def start_stream(self, symbol: str):
        # todo: support multiple symbols
        self.tickers[symbol.upper()] = float()  # will be used to store latest price of ticker
        full_path = self._BASE_WS + f"/stream?streams={symbol.lower()}@aggTrade"

        session = aiohttp.ClientSession()
        ws = await session.ws_connect(full_path)

        while True:
            msg = await ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                msg = msg.json()
                print(msg)
                self.trade_stream_parser(msg['data'])

            else:
                print("error")
                # todo: handle errors
            await asyncio.sleep(0.01)

    def trade_stream_parser(self, msg: dict):
        """callback for stream to parse trades msgs"""
        ticker_name, last_price = msg['s'], msg['p']

        self.tickers[ticker_name] = float(last_price)

    def get_price(self, symbol):
        return self.tickers[symbol]

