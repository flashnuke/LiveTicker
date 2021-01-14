from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from PriceFetcher import Fetcher
from threading import Thread
from time import sleep

# todo: refractor symbol stream
# todo: kill previous stream
# todo: reset total pnl button


class MainApp(App):
    """
    _EX = exchange (for now hard coded to 'Binance')
    _SYM = symbol (for now hard coded to 'btcusdt')

    current_position - current position being held (1 for long, -1 for short, 0 for none)
    entry_price - entry price for current position
    last_price
    zero_pnl - macro string used to reset PnL
    cumulative_pnl - PnL of all positions
    current_pnl - PnL of current position being held
    position_mapping - convert from int to str representation of position type
    """
    _EX = "Binance"
    _SYM = "btcusdt"

    price_fetcher = Fetcher(_EX)
    current_position = int()
    entry_price = float()
    last_price = float()
    zero_pnl = "0.00%"
    cumulative_pnl = 0.0
    current_pnl = 0.0

    position_mapping = {
        1: 'Long',
        0: 'Neutral',
        -1: 'Short'
    }

    def build(self):
        """
        main_layout
            price_label - live price feed
            pnl_label - live PnL of current position
            entry_price_status_layout
                pos_str_label - string representation of current position
                entry_price_label - entry price of current position
            total_pnl_layout
                status_label - a string containing 'Total PnL'
                cum_pnl_label - the cumulative PnL
            buttons_layout
                button_buy
                button_sell
        """
        main_layout = BoxLayout(orientation="vertical")
        self.price_label = Label(text='0.0',
                                 bold=True,
                                 size_hint=(.8, .8),
                                 font_size=250,
                                 pos_hint={'center_x': .5, 'center_y': .9})
        main_layout.add_widget(self.price_label)  # add price label

        self.pnl_label = Label(text=self.zero_pnl,
                               bold=True,
                               size_hint=(.5, .5),
                               font_size=100,
                               pos_hint={'center_x': .5, 'center_y': .9})
        main_layout.add_widget(self.pnl_label)  # add price label

        entry_price_status_layout = BoxLayout(orientation='horizontal')
        self.pos_str_label = Label(text='',
                                   bold=True,
                                   size_hint=(.5, .5),
                                   font_size=50,
                                   pos_hint={'center_x': .5, 'center_y': .9})
        entry_price_status_layout.add_widget(self.pos_str_label)  # add price label
        self.update_position_label()
        self.entry_price_label = Label(text='0.00',
                                       italic=True,
                                       size_hint=(.5, .5),
                                       font_size=50,
                                       pos_hint={'center_x': .5, 'center_y': .9})
        entry_price_status_layout.add_widget(self.entry_price_label)  # add price label
        main_layout.add_widget(entry_price_status_layout)

        total_pnl_layout = BoxLayout(orientation="horizontal")
        self.status_label = Label(text='Total PnL',
                                  size_hint=(.5, .5),
                                  font_size=85,
                                  pos_hint={'center_x': .5, 'center_y': .9})
        total_pnl_layout.add_widget(self.status_label)  # add price label
        self.cum_pnl_label = Label(text='',
                                   bold=True,
                                   size_hint=(.5, .5),
                                   font_size=85,
                                   pos_hint={'center_x': .5, 'center_y': .9})
        total_pnl_layout.add_widget(self.cum_pnl_label)  # add price label
        self.update_cum_pnl_label()
        main_layout.add_widget(total_pnl_layout)

        buttons_layout = BoxLayout(orientation="horizontal",
                                   size_hint=(1, 0.3))
        button_buy = Button(text='Buy',
                            size_hint=(.8, .8),
                            pos_hint={'center_x': .5, 'center_y': .8},
                            background_color=get_color_from_hex("#3de03a"))
        button_buy.bind(on_press=self.on_press_buy)
        buttons_layout.add_widget(button_buy)

        button_sell = Button(text='Sell',
                             size_hint=(.8, .8),
                             pos_hint={'center_x': .5, 'center_y': .8},
                             background_color=get_color_from_hex("#eb3838"))
        button_sell.bind(on_press=self.on_press_sell)
        buttons_layout.add_widget(button_sell)

        main_layout.add_widget(buttons_layout)

        self.start_ticker(self._SYM)

        return main_layout

    def start_ticker(self, symbol: str):
        """
        start a new ticker on a new thread
        * fetches all tickers and verifies symbol exists
        * passes `self.on_price_update` as the callback method
        """
        if symbol.upper() in self.price_fetcher.get_all_symbols():
            Thread(target=self.price_fetcher.connect_ws, args=(symbol, self.on_price_update), daemon=True).start()
            while not self.last_price:
                sleep(0.05)
        else:
            raise Exception(f"ticker {symbol} does not exist")

    def stop_ticker(self, symbol: str):
        """
        stop ticker (kill stream and thread)
        """
        self.price_fetcher.disconnect_ws(symbol)

    def on_press_sell(self, instance):
        """
        if no pos - enter short
        if long - close pos
        """
        if self.current_position == 0:
            self.current_position = -1
            self.entry_price = self.last_price

        elif self.current_position == 1:
            self.reset_position()

        self.update_status_labels()

    def update_status_labels(self):
        """
        updates:
        * entry price label
        * position label
        * cumulative pnl label
        """
        self.update_entry_label()
        self.update_position_label()
        self.update_cum_pnl_label()

    def reset_position(self):
        """
        * updates cumulative pnl
        * resets position status
        * resets entry price
        * resets pos pnl
        """
        self.cumulative_pnl += self.current_pnl
        self.current_position = 0
        self.entry_price = 0
        self.reset_pnl()

    def reset_pnl(self):
        """Reset pnl label"""
        self.pnl_label.text = self.zero_pnl
        self.pnl_label.color = get_color_from_hex("#ffffff")

    def on_press_buy(self, instance):
        """
        if no pos - enter long
        if short - close pos
        """
        if self.current_position == 0:
            self.current_position = 1
            self.entry_price = self.last_price

        elif self.current_position == -1:
            self.reset_position()

        self.update_status_labels()

    def on_price_update(self, price):
        """
        will be passed as callback to ws stream
        """
        self.update_pnl(price)
        self.price_label.text = str(price)
        if price > self.last_price:
            self.price_label.color = get_color_from_hex("#00b82b")
        else:
            self.price_label.color = get_color_from_hex("#b80000")

        self.last_price = price

    def update_pnl(self, price):
        """
        calculates current position PnL and updates the label accordingly
        """
        if self.current_position != 0:
            self.current_pnl = self.entry_price / price
            self.current_pnl = round((self.current_pnl - 1) * 100, 2) if self.current_position == -1 else \
                round((1 - self.current_pnl) * 100, 2)

            self.pnl_label.text = str(f"{self.current_pnl}%")
            if self.current_pnl > 0:
                self.pnl_label.color = get_color_from_hex("#00b82b")
            elif self.current_pnl < 0:
                self.pnl_label.color = get_color_from_hex("#b80000")
            else:
                self.reset_pnl()

    def update_entry_label(self):
        """
        Updates the entry price label
        """
        self.entry_price_label.text = str(self.entry_price)

    def update_position_label(self):
        """
        Updates current position label
        """
        self.pos_str_label.text = self.position_mapping[self.current_position]
        if self.current_position > 0:
            self.pos_str_label.color = get_color_from_hex("#00b82b")
        elif self.current_position < 0:
            self.pos_str_label.color = get_color_from_hex("#b80000")
        else:
            self.pos_str_label.color = get_color_from_hex("#ffffff")

    def update_cum_pnl_label(self):
        """
        Updates cumulative PNL label
        """
        self.cum_pnl_label.text = f"{round(self.cumulative_pnl, 2)}%"
        if self.cumulative_pnl > 0:
            self.cum_pnl_label.color = get_color_from_hex("#00b82b")
        elif self.cumulative_pnl < 0:
            self.cum_pnl_label.color = get_color_from_hex("#b80000")
        else:
            self.cum_pnl_label.color = get_color_from_hex("#ffffff")


if __name__ == "__main__":
    app = MainApp()
    app.run()
