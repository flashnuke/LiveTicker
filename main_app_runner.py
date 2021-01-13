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
    last_price = float()  # to know how to color it based on tick change
    zero_pnl = "0.00%"
    cumulative_pnl = 0.0
    current_pnl = 0.0

    position_mapping = {
        1: 'Long',
        0: 'Neutral',
        -1: 'Short'
    }

    # todo: reset position method
    # todo: total pnl colored and pos colored
    # todo: on close - terminate all threads

    def build(self):
        main_layout = BoxLayout(orientation="vertical")
        self.price_label = Label(text='0.0',
                                 size_hint=(.8, .8),
                                 font_size=100,
                                 pos_hint={'center_x': .5, 'center_y': .9})
        main_layout.add_widget(self.price_label)  # add price label

        Thread(target=self.price_fetcher.connect_ws, args=(_SYM, self.on_price_update)).start()
        while not self.last_price:
            time.sleep(0.05)

        self.pnl_label = Label(text=self.zero_pnl,
                               size_hint=(.5, .5),
                               font_size=20,
                               pos_hint={'center_x': .5, 'center_y': .9})
        main_layout.add_widget(self.pnl_label)  # add price label

        entry_price_status_layout = BoxLayout(orientation='horizontal')
        self.pos_str_label = Label(text='',
                                   size_hint=(.5, .5),
                                   font_size=20,
                                   pos_hint={'center_x': .5, 'center_y': .9})
        entry_price_status_layout.add_widget(self.pos_str_label)  # add price label
        self.update_position_label()
        self.entry_price_label = Label(text='0.00',
                                       size_hint=(.5, .5),
                                       font_size=20,
                                       pos_hint={'center_x': .5, 'center_y': .9})
        entry_price_status_layout.add_widget(self.entry_price_label)  # add price label
        main_layout.add_widget(entry_price_status_layout)

        total_pnl_layout = BoxLayout(orientation="horizontal")
        self.status_label = Label(text='Total PnL',
                                  size_hint=(.5, .5),
                                  font_size=35,
                                  pos_hint={'center_x': .5, 'center_y': .9})
        total_pnl_layout.add_widget(self.status_label)  # add price label
        self.status_pnl_label = Label(text='',
                                      size_hint=(.5, .5),
                                      font_size=35,
                                      pos_hint={'center_x': .5, 'center_y': .9})
        total_pnl_layout.add_widget(self.status_pnl_label)  # add price label
        self.update_status_label()
        main_layout.add_widget(total_pnl_layout)

        buttons_layout = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.3))
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

    def reset_pnl(self):
        """Reset pnl label"""
        self.pnl_label.text = self.zero_pnl
        self.pnl_label.color = get_color_from_hex("#ffffff")

    def on_press_sell(self, instance):
        """
        if no pos - enter short
        if long - close pos
        """
        if self.current_position == 0:
            self.current_position = -1
            self.entry_price = self.last_price

        elif self.current_position == 1:
            self.cumulative_pnl += self.current_pnl
            self.current_position = 0
            self.entry_price = 0
            self.reset_pnl()

        self.update_entry_label()
        self.update_position_label()
        self.update_status_label()

    def on_press_buy(self, instance):
        """
        if no pos - enter long
        if short - close pos
        """
        if self.current_position == 0:
            self.current_position = 1
            self.entry_price = self.last_price

        elif self.current_position == -1:
            self.cumulative_pnl += self.current_pnl
            self.current_position = 0
            self.entry_price = 0
            self.reset_pnl()

        self.update_entry_label()
        self.update_position_label()
        self.update_status_label()

    def on_price_update(self, price):
        """will be passed as callback to ws stream"""
        self.update_pnl(price)
        self.price_label.text = str(price)
        if price > self.last_price:
            self.price_label.color = get_color_from_hex("#00b82b")
        else:
            self.price_label.color = get_color_from_hex("#b80000")

        self.last_price = price

    def update_pnl(self, price):
        # todo: define
        if self.current_position != 0:
            self.current_pnl = self.entry_price / price
            self.current_pnl = round((self.current_pnl - 1) * 100, 2)
            self.pnl_label.text = str(f"{self.current_pnl}%")
            if self.current_pnl > 0:
                self.pnl_label.color = get_color_from_hex("#00b82b")
            elif self.current_pnl < 0:
                self.pnl_label.color = get_color_from_hex("#b80000")
            else:
                self.reset_pnl()

    def update_entry_label(self):
        # todo: define
        self.entry_price_label.text = str(self.entry_price)

    def update_position_label(self):
        # todo: define
        self.pos_str_label.text = self.position_mapping[self.current_position]

    def update_status_label(self):
        """constructs status string"""
        self.status_pnl_label.text = f"{round(self.cumulative_pnl, 2)}%"


if __name__ == "__main__":
    _EX = "Binance"
    _SYM = "btcusdt"
    app = MainApp()
    app.run()
