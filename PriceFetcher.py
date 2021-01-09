from utils.BinanceFetcher import Binance
import asyncio
import aiohttp


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

    def fetch_price(self, symbol: str):
        """
        if connected ws, will simply return price.
        else: use REST
        """
        return self.exchange_manager.get_price(symbol)

    async def connect_ws(self, symbol: str):
        await self.exchange_manager.start_stream(symbol)


async def price_fetcher(x: Fetcher, symbol: str):
    while True:
        print(x.fetch_price(symbol))
        await asyncio.sleep(0.5)


async def runner():
    x = Fetcher('Binance')
    symbol = 'btcusdt'
    await asyncio.gather(x.connect_ws(symbol), price_fetcher(x, symbol))

if __name__ == "__main__":
    asyncio.run(runner())
