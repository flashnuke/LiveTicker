import asyncio
import requests as r
from collections import deque
from time import time


class NewsFetcher:
    """
    _K - k
    _BASE - path base
    _CAT - category for news
    _NEWS_ENDP - news endpoint
    _LENGTH - max num of news to maintain
    _INTERVAL - interval between api fetches

    self.news_deque - will store news in deque
    self.last_update - flag to maintain track of last fetch time
    self.main_eventloop - use the same event loop to avoid race condition
    self.latest_id - maintain track of latest news id to avoid fetching the same data
    self.status - use this flag to kill manager loop
    """

    _K = "c0noo6v48v6t5mebkbl0"  # don't worry, this is a free k :)
    _BASE = "https://finnhub.io/api/v1"
    _CAT = "crypto"
    _NEWS_ENDP = "/news"
    _LENGTH = 5
    _INTERVAL = 60

    def __init__(self):
        self.full_path = f"{self._BASE}/{self._NEWS_ENDP}?category={self._CAT}&token={self._K}"
        self.news_deque = deque(maxlen=self._LENGTH)
        self.last_update = 0
        self.main_eventloop = asyncio.new_event_loop()
        self.latest_id = 0
        self.status = False

    async def fetch_news(self):
        """
        make the request and parse response into deque
        save latest news id to avoid fetching the same over and over
        """
        path = self.full_path + f"&minId={self.latest_id}"
        request = r.get(url=path)
        news = request.json()

        for entry in news:
            news_id = int(entry['id'])
            self.latest_id = max(news_id, self.latest_id)

            record = dict()
            record["news_id"] = news_id
            record["news_content"] = f"{entry['source']} -- {entry['headline']} -- {entry['summary']}"
            self.news_deque.append(record)

    async def updates_pusher(self, cb_ptr, status):
        """
        will receive the callback from the main app and push updates
        """
        now = time()
        if now - self.last_update > self._INTERVAL:
            await self.fetch_news()
            self.last_update = now

        for record in self.news_deque:
            if not status:
                break
            cb_ptr(record["news_content"])

    def news_manager(self, cb_ptr, status: bool):
        """
        runner for entire class
        status and cb_ptr are passed from main app

        use class attr eventloop to avoid race condition
        """
        self.status = True
        while self.status:
            self.main_eventloop.run_until_complete(self.updates_pusher(cb_ptr, status))

    def turn_off(self):
        """
        turn off using status class attr
        """
        self.status = False
