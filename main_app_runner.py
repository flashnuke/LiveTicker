from kivy.app import App
from kivy.uix.button import Button
from PriceFetcher import Fetcher
import asyncio
from threading import Thread


class MainApp(App):
    def build(self):
        self.price_fetcher = Fetcher('Binance')

        button = Button(text='Click here to fetch price',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})

        button.bind(on_press=self.on_press_button)

        return button

    def on_press_button(self, instance):
        price = self.price_fetcher.fetch_price(_SYM, use_rest=True)
        print(f"Current price is {price}")


if __name__ == "__main__":
    _EX = "Binance"
    _SYM = "btcusdt"
    app = MainApp()
    app.run()