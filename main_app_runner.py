from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from PriceFetcher import Fetcher
from threading import Thread
import time
from kivy.utils import get_color_from_hex

class MainApp(App):
    price_fetcher = Fetcher('Binance')
    current_position = int()  # 1 for long, -1 for short, 0 for none
    entry_price = float()  # entry price for current position
    current_pnl = float()  # current pnl
    # todo: on close - terminate all threads
    # todo: if up then green, else red (both pnl and price)

    def build(self):
        main_layout = BoxLayout(orientation="vertical")
        self.label = Label(text='0',
                           size_hint=(.8, .8),
                           font_size=100,
                           pos_hint={'center_x': .5, 'center_y': .5})

        Thread(target=self.price_fetcher.connect_ws, args=(_SYM, self.on_price_update)).start()
        main_layout.add_widget(self.label)  # add price label

        buttons_layout = BoxLayout(orientation="horizontal")
        button_buy = Button(text='Buy',
                            size_hint=(.5, .5),
                            pos_hint={'center_x': .3, 'center_y': .3},
                            background_color=get_color_from_hex("#3de03a"))
        button_buy.bind(on_press=self.on_press_buy)
        buttons_layout.add_widget(button_buy)

        button_sell = Button(text='Sell',
                             size_hint=(.5, .5),
                             pos_hint={'center_x': .3, 'center_y': .3},
                             background_color=get_color_from_hex("#eb3838"))
        button_sell.bind(on_press=self.on_press_sell)
        buttons_layout.add_widget(button_sell)

        main_layout.add_widget(buttons_layout)

        return main_layout

    def on_press_sell(self, instance):
        print(f"pressed sell")

    def on_press_buy(self, instance):
        print(f"pressed buy")

    def on_price_update(self, price):
        """will be passed as callback to ws stream"""
        self.label.text = str(price)


if __name__ == "__main__":
    _EX = "Binance"
    _SYM = "btcusdt"
    app = MainApp()
    app.run()
    # app.price_fetcher.connect_ws(_SYM)