from kivy.app import App
from kivy.uix.button import Button
from PriceFetcher import Fetcher
import asyncio
from threading import Thread


class MainApp(App):
    def build(self):
        self.price_fetcher = Fetcher('Binance')
        symbol = 'btcusdt'
        Thread(asyncio.run(self.runner(self.price_fetcher, symbol))).start()

        button = Button(text='Hello from Kivy',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})

        button.bind(on_press=self.on_press_button)

        return button

    def on_press_button(self, instance):
        print('You pressed the button!')

    @staticmethod
    async def runner(fetcher, symbol):
        await asyncio.gather(fetcher.connect_ws(symbol))


if __name__ == "__main__":
    app = MainApp()
    app.run()