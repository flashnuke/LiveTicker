import asyncio
import aiohttp
from collections import deque
from time import sleep


class NewsFetcher:
    _K = "c0noo6v48v6t5mebkbl0"  # don't worry, this is a k :)
    _BASE = "https://finnhub.io/api/v1"
    _CAT = "crypto"
    _NEWS_ENDP = "/news"

    _LENGTH = 5

    _INTERVAL = 60

    def __init__(self):
        self.full_path = f"{self._BASE}/{self._NEWS_ENDP}?category={self._CAT}&token={self._K}"
        self.params = {"toke"}
        self.news_deque = deque(maxlen=self._LENGTH)

    async def fetch_news(self):
        """
        make the request and parse response into deque
        """
        async with aiohttp.ClientSession() as session:
            async with await session.get(url=self.full_path) as res:
                news = await res.json()

                for entry in news:
                    record = dict()
                    record["news_id"] = entry['id']
                    record["news_content"] = f"{entry['source']} -- {entry['headline']} -- {entry['summary']}"
                    self.news_deque.append(record)

    async def updates_pusher(self, cb_ptr):
        """
        will receive the callback from the main app and push updates
        """
        await self.fetch_news()
        for record in self.news_deque:
            cb_ptr(record["news_content"])

        await asyncio.sleep(self._INTERVAL)

    def news_manager(self, cb_ptr):
        """
        runner for entire class
        """
        while True:
            asyncio.new_event_loop().run_until_complete(self.updates_pusher(cb_ptr))
