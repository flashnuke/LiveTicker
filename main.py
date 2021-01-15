from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from PriceFetcher import Fetcher
from threading import Thread
from time import sleep

# from kivy.config import Config
# Config.set('graphics', 'width', '412')
# Config.set('graphics', 'height', '915')


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
    _SYM = "BTCUSDT"

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
        main_layout  (used as class attr)
            price_label - live price feed
            pnl_label - live PnL of current position
            entry_price_status_layout
                pos_str_label - string representation of current position
                entry_price_label - entry price of current position
            options_layout - to add padding to the button
                button_refresh - a refresh button for the cumulative PnL
                button_settings - a button to open settings menu
                    popup_settings - a popup window for settings
                        symbols_list -  dropdown list for symbols
                cum_pnl_label
            position_buttons_layout
                button_buy
                button_sell
        """
        self.main_layout = BoxLayout(orientation="vertical")
        self.price_label = Label(text='0.0',
                                 bold=True,
                                 size_hint=(.8, .8),
                                 font_size=250,
                                 pos_hint={'center_x': .5, 'center_y': .9})
        self.main_layout.add_widget(self.price_label)  # add price label

        self.pnl_label = Label(text=self.zero_pnl,
                               bold=True,
                               size_hint=(.5, .5),
                               font_size=100,
                               pos_hint={'center_x': .5, 'center_y': .9})
        self.main_layout.add_widget(self.pnl_label)  # add price label

        entry_price_status_layout = BoxLayout(orientation='horizontal')
        self.pos_str_label = Label(text='',
                                   bold=True,
                                   size_hint=(.5, .5),
                                   font_size=60,
                                   pos_hint={'center_x': .5, 'center_y': .9})
        entry_price_status_layout.add_widget(self.pos_str_label)  # add price label
        self.update_position_label()
        self.entry_price_label = Label(text='0.00',
                                       italic=True,
                                       size_hint=(.5, .5),
                                       font_size=60,
                                       pos_hint={'center_x': .5, 'center_y': .9})
        entry_price_status_layout.add_widget(self.entry_price_label)  # add price label
        self.main_layout.add_widget(entry_price_status_layout)

        options_layout = BoxLayout(orientation="horizontal",
                                   # padding=[200, 100, 100, 100],
                                   pos_hint={'center_x': 0.6, 'center_y': 0.5},
                                   spacing=100)
        button_settings = Button(text='',
                                 size_hint=(None, None),
                                 size=(170, 170),
                                 pos_hint={'center_x': .5, 'center_y': .5},
                                 background_normal='icons/settings_icon.png',
                                 background_down='icons/settings_icon.png')
        button_settings.bind(on_press=self.on_press_settings)
        options_layout.add_widget(button_settings)
        button_refresh = Button(text='',
                                size_hint=(None, None),
                                size=(170, 170),
                                pos_hint={'center_x': .5, 'center_y': .5},
                                background_normal='icons/refresh_icon.png',
                                background_down='icons/refresh_icon.png')
        button_refresh.bind(on_press=self.on_press_refresh)
        options_layout.add_widget(button_refresh)
        self.cum_pnl_label = Label(text='',
                                   bold=True,
                                   size_hint=(.5, .5),
                                   font_size=140,
                                   pos_hint={'center_x': .5, 'center_y': .5})
        options_layout.add_widget(self.cum_pnl_label)
        self.update_cum_pnl_label()

        self.main_layout.add_widget(options_layout)

        position_buttons_layout = BoxLayout(orientation="horizontal",
                                            size_hint=(1, 0.5))
        button_buy = Button(text='Buy',
                            size_hint=(.8, .8),
                            pos_hint={'center_x': .5, 'center_y': .8},
                            background_color=get_color_from_hex("#3de03a"))
        button_buy.bind(on_press=self.on_press_buy)
        position_buttons_layout.add_widget(button_buy)

        button_sell = Button(text='Sell',
                             size_hint=(.8, .8),
                             pos_hint={'center_x': .5, 'center_y': .8},
                             background_color=get_color_from_hex("#eb3838"))
        button_sell.bind(on_press=self.on_press_sell)
        position_buttons_layout.add_widget(button_sell)

        self.main_layout.add_widget(position_buttons_layout)

        self.start_ticker(self._SYM)

        self.popup_settings = Popup(title='Settings',
                                    size_hint=(0.5, 0.5),
                                    background_color=[0, 0, 0, .9])

        self.symbols_dropdown = DropDown(max_height=650)
        for symbol in self.price_fetcher.get_all_symbols():
            symbol_button = Button(text=symbol.upper(), size_hint_y=None, height=125)
            symbol_button.bind(on_release=lambda symbol_button: self.symbols_dropdown.select(symbol_button.text))
            self.symbols_dropdown.add_widget(symbol_button)

        self.main_symbol_button = Button(text=self._SYM.upper(),
                                         size_hint=(0.5, 0.2),
                                         pos_hint={'center_x': .5, 'center_y': .8})
        self.main_symbol_button.bind(on_release=self.symbols_dropdown.open)
        self.symbols_dropdown.bind(on_select=self.change_ticker)

        self.popup_settings.add_widget(self.main_symbol_button)

        return self.main_layout

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

    def change_ticker(self, instance, new_symbol: str):
        """
        disconnects old symbol stream and connects a new one
        uses first fetch via REST for illiquid pairs
        """
        self.stop_ticker(self._SYM)
        self.reset_pnl()
        self.reset_position()

        self._SYM = new_symbol
        self.on_price_update(self.price_fetcher.fetch_price(self._SYM, use_rest=True))
        self.start_ticker(new_symbol)
        self.main_symbol_button.text = new_symbol

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

    def on_press_refresh(self, instance):
        """
        when pressing refresh button
        """
        self.reset_cum_pnl()

    def on_press_settings(self, instance):
        """
        when pressing settings button
        """
        self.open_settings_menu()

    def open_settings_menu(self):
        """
        opens the settings popup menu
        """
        self.popup_settings.open()

    def reset_cum_pnl(self):
        """
        resets cumulative pnl
        """
        self.cumulative_pnl = 0.0
        self.update_cum_pnl_label()

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
        self.update_position_label()
        self.update_entry_label()

    def reset_pnl(self):
        """Reset pnl label"""
        self.pnl_label.text = self.zero_pnl
        self.pnl_label.color = get_color_from_hex("#ffffff")

    def on_price_update(self, price):
        """
        will be passed as callback to ws stream
        """
        self.update_pnl(price)
        precision = self.price_fetcher.get_symbol_precision(self._SYM)
        self.price_label.text = f'{price:.{precision}f}'
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
        precision = self.price_fetcher.get_symbol_precision(self._SYM)
        self.entry_price_label.text = f'{self.entry_price:.{precision}f}'

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
