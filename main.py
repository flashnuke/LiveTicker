from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore
from PriceFetcher import Fetcher
from utils.NewsFetcher import NewsFetcher
from threading import Thread
from time import sleep
import webbrowser

from utils import Pulser

# from kivy.config import Config
# Config.set('graphics', 'width', '412')
# Config.set('graphics', 'height', '915')


class MainApp(App):
    """
    _DEF_EX = exchange (for now hard coded to 'Binance')
    _DEF_SYM = symbol (for now default is 'btcusdt')
    _DARK_MODE_RGB = RGB for dark mode
    _LIGHT_MODE_RGB = RGB for light mode
    _DEF_MODE = default view mode
    _DEFAULT_NEWS_MODE = default status for displaying news
    _DEF_CUM_PNL = default cumulative pnl
    _DEFAULT_FEES = default user fees
    _PNL_PERC = decimal percision for pnl display
    _DEF_DATAJSON_NAME = json filename for user settings

    current_position - current position being held (1 for long, -1 for short, 0 for none)
    entry_price - entry price for current position
    last_price
    zero_pnl - macro string used to reset PnL
    cumulative_pnl - PnL of all positions
    current_pnl - PnL of current position being held

    position_mapping - convert from int to str representation of position type
    display_mode_mapping - convert from integer to str representation of display mode

    _GIT_URL -  the developer's GITHUB url
    about_info - the text to be displayed in the about window
    """
    _DARK_MODE_RGB = (0, 0, 0)
    _TEXT_COLOR_DARKMODE = get_color_from_hex("#ffffff")
    _LIGHT_MODE_RGB = (227 / 255, 214 / 255, 177 / 255)
    _TEXT_COLOR_LIGHTMODE = get_color_from_hex("#000000")
    _DEF_EX = "Binance"
    _DEF_SYM = "BTCUSDT"
    _DEF_DISP_MODE = 0
    _DEFAULT_NEWS_MODE = True
    _DEF_CUM_PNL = 0.0
    _DEFAULT_FEES = 0.0
    _PNL_PERC = 2
    _DEF_DATAJSON_NAME = "user_data"

    _GREEN_HEX = "#00b82b"
    _RED_HEX = "#b80000"

    price_fetcher = Fetcher(_DEF_EX)
    current_position = int()
    entry_price = float()
    last_price = float()
    zero_pnl = "0.00%"
    current_pnl = 0.0

    position_mapping = {
        1: 'Long',
        0: 'Neutral',
        -1: 'Short'
    }

    display_mode_mapping = {
        0: 'Dark Mode',
        1: 'Light Mode'
    }

    _GIT_URL = "https://github.com/adanikel"
    about_info = f'This is an open source game designed to ' \
                 f'simulate real-life trading by fetching a live price feed ' \
                 f'from top crypto exchanges (currently only Binance is supported).' \
                 f'\n\n\n' \
                 f'Made by [ref={_GIT_URL}][color=0000ff]adanikel[/color][/ref]'

    def build(self):
        """
        main_layout  (used as class attr)
            symbol_label - see current symbol
            price_label - live price feed
            pnl_label - live PnL of current position
            entry_price_status_layout
                pos_str_label - string representation of current position
                entry_price_label - entry price of current position
            news_label - news flash
            options_layout - to add padding to the button
                button_refresh - a refresh button for the cumulative PnL
                button_settings - a button to open settings menu
                    popup_settings - a popup window for settings
                        symbols_list -  dropdown list for symbols
                        button_display_mode - toggle view mode (dark or light)
                        button_news - turn on / off newsflash
                        button_fees - popup page to fees
                            fees_label - display fees
                            fees_up_button - increment fees
                            fees_down_button - decrement fees
                        button_about - display about
                cum_pnl_label
            position_buttons_layout
                button_buy
                button_sell
        """

        self.store = JsonStore(f'{self._DEF_DATAJSON_NAME}.json')
        self.load_user_data()

        self.main_layout = BoxLayout(orientation="vertical")

        self.main_layout.add_widget(Pulser.bg_pulser)
        with self.main_layout.canvas:
            Rectangle(source="icons/lightning.png", size=(1450, 1450), pos=(0, 550))
        self.symbol_label = Label(text='',
                                  bold=True,
                                  size_hint=(.5, .5),
                                  font_size=100,
                                  pos_hint={'center_x': .5, 'center_y': 1},
                                  color=(237 / 255, 142 / 255, 43 / 255, 0.4))
        self.main_layout.add_widget(self.symbol_label)  # add price label

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
        self.entry_price_label = Label(text='0.00',
                                       italic=True,
                                       size_hint=(.5, .5),
                                       font_size=60,
                                       pos_hint={'center_x': .5, 'center_y': .9})
        entry_price_status_layout.add_widget(self.entry_price_label)  # add price label
        self.main_layout.add_widget(entry_price_status_layout)

        self.news_label = Label(text='',
                                size_hint=(.5, .5),
                                font_size=60,
                                pos=(0, 0))
        self.main_layout.add_widget(self.news_label)

        options_layout = BoxLayout(orientation="horizontal",
                                   # padding=[200, 100, 100, 100],
                                   pos_hint={'center_x': 0.6, 'center_y': 0.5},
                                   spacing=100)
        self.button_settings = Button(text='',
                                      size_hint=(None, None),
                                      size=(170, 170),
                                      pos_hint={'center_x': .5, 'center_y': .5})
        self.button_settings.bind(on_press=self.on_press_settings)
        options_layout.add_widget(self.button_settings)
        self.button_refresh = Button(text='',
                                     size_hint=(None, None),
                                     size=(170, 170),
                                     pos_hint={'center_x': .5, 'center_y': .5})
        self.button_refresh.bind(on_press=self.on_press_refresh)
        options_layout.add_widget(self.button_refresh)
        self.cum_pnl_label = Label(text='',
                                   bold=True,
                                   size_hint=(.5, .5),
                                   font_size=140,
                                   pos_hint={'center_x': .5, 'center_y': .5})
        options_layout.add_widget(self.cum_pnl_label)

        self.main_layout.add_widget(options_layout)

        position_buttons_layout = BoxLayout(orientation="horizontal",
                                            size_hint=(1, 0.5))
        button_buy = Button(text='Buy',
                            bold=True,
                            size_hint=(.8, .8),
                            pos_hint={'center_x': .5, 'center_y': .8},
                            background_color=get_color_from_hex("#3de03a"))
        button_buy.bind(on_press=self.on_press_buy)
        position_buttons_layout.add_widget(button_buy)

        button_sell = Button(text='Sell',
                             bold=True,
                             size_hint=(.8, .8),
                             pos_hint={'center_x': .5, 'center_y': .8},
                             background_color=get_color_from_hex("#eb3838"))
        button_sell.bind(on_press=self.on_press_sell)
        position_buttons_layout.add_widget(button_sell)

        self.main_layout.add_widget(position_buttons_layout)

        self.start_ticker(self.current_symbol)

        self.popup_settings = Popup(title='Settings',
                                    size_hint=(0.5, 0.5),
                                    background='icons/secondary_background.png',
                                    background_color=[1, 1, 1, .5],
                                    on_dismiss=self.save_user_data)
        self.settings_buttons = BoxLayout(orientation="vertical", padding=[0, 0, 0, 700])  # in pc, use 100

        self.symbols_dropdown = DropDown(max_height=650)
        for symbol in self.price_fetcher.get_all_symbols():
            symbol_button = Button(text=symbol.upper(), size_hint_y=None, height=125)
            symbol_button.bind(on_release=lambda symbol_button: self.symbols_dropdown.select(symbol_button.text))
            self.symbols_dropdown.add_widget(symbol_button)

        self.main_symbol_button = Button(text=self.current_symbol.upper(),
                                         pos_hint={'center_x': .5, 'center_y': .8})
        self.main_symbol_button.bind(on_release=self.symbols_dropdown.open)
        self.symbols_dropdown.bind(on_select=self.change_ticker)

        self.settings_buttons.add_widget(self.main_symbol_button)

        self.button_display_mode = Button(text='',
                                          pos_hint={'center_x': .5, 'center_y': .5})
        self.button_display_mode.bind(on_press=self.set_display_mode)
        self.settings_buttons.add_widget(self.button_display_mode)

        self.about_label = Label(text=self.about_info,
                                 markup=True,
                                 on_ref_press=self.on_ref_press,
                                 pos_hint={'center_x': .5, 'center_y': 1})
        self.about_label.bind(size=lambda s, w: s.setter('text_size')(s, w))  # to limit text into popup

        self.about_window = Popup(title='About',
                                  size_hint=(0.5, 0.5),
                                  background_color=[1, 1, 1, .5],
                                  content=self.about_label)

        self.news_fetcher = NewsFetcher()
        self.button_news = Button(text=self.generate_news_button_text(),
                                   pos_hint={'center_x': .5, 'center_y': .5})
        self.button_news.bind(on_press=self.on_press_news)
        self.settings_buttons.add_widget(self.button_news)
        if self.news_status:
            self.start_news_flasher()

        self.fees_layout = BoxLayout(orientation='horizontal',
                                     padding=[10, 0, 10, 0])
        self.fees_label = Label(text='',
                                pos_hint={'center_x': .9, 'center_y': .9},
                                size_hint=(0.1, 0.1))
        self.update_fees_label()
        self.fees_layout.add_widget(self.fees_label)

        self.fees_up = Button(text='+',
                              pos_hint={'center_x': .9, 'center_y': .9},
                                size_hint=(0.03, 0.1))
        self.fees_up.bind(on_press=self.on_press_fees_up)
        self.fees_layout.add_widget(self.fees_up)

        self.fees_down = Button(text='-',
                              pos_hint={'center_x': .9, 'center_y': .9},
                                size_hint=(0.03, 0.1))
        self.fees_down.bind(on_press=self.on_press_fees_down)
        self.fees_layout.add_widget(self.fees_down)

        self.fees_window = Popup(title='Fees',
                                  size_hint=(0.5, 0.5),
                                  background_color=[1, 1, 1, .5],
                                  content=self.fees_layout)
        self.button_fees = Button(text='Fees',
                                  pos_hint={'center_x': .5, 'center_y': .5})
        self.button_fees.bind(on_press=self.on_press_fees)
        self.settings_buttons.add_widget(self.button_fees)

        self.button_about = Button(text='About',
                                   pos_hint={'center_x': .5, 'center_y': .5})
        self.button_about.bind(on_press=self.on_press_about)
        self.settings_buttons.add_widget(self.button_about)

        self.popup_settings.add_widget(self.settings_buttons)

        self.set_display_mode(None, load_up=True)
        self.reset_pnl()  # for display mode text
        self.update_symbol_label()  # set up label

        return self.main_layout

    def load_user_data(self):
        """
        loads caches user data from last run
        """
        if self.store.exists(self._DEF_DATAJSON_NAME):
            try:
                data = self.store.get(self._DEF_DATAJSON_NAME)
                self._DEF_SYM = data['_SYM']
                self._DEF_DISP_MODE = data['_DEF_DISP_MODE']
                self._DEFAULT_NEWS_MODE = data['_DEFAULT_NEWS_MODE']
                self._DEFAULT_FEES = data['_DEFAULT_FEES']
                self.cumulative_pnl = data['cum_pnl']
            except KeyError:
                pass  # no data will be loaded

        self.apply_user_data()

    def apply_user_data(self):
        """
        applies default / loaded settings to current run
        """
        self.current_symbol = self._DEF_SYM
        self.current_display_mode = self._DEF_DISP_MODE
        self.news_status = self._DEFAULT_NEWS_MODE
        self.user_fees = self._DEFAULT_FEES
        self.cumulative_pnl = self._DEF_CUM_PNL

    def save_user_data(self, *args):
        """
        save current data
        """
        self.store.put(self._DEF_DATAJSON_NAME,
                       _SYM=self.current_symbol,
                       _DEF_DISP_MODE=self.current_display_mode,
                       _DEFAULT_NEWS_MODE=self.news_status,
                       _DEFAULT_FEES=self.user_fees,
                       cum_pnl=self.cumulative_pnl)

    def start_news_flasher(self):
        """
        will be triggered upon button press and at launch
        """
        Thread(target=self.news_fetcher.news_manager, args=(self.flash_news, self.news_status), daemon=True).start()

    def reset_news_label(self):
        """
        set back to empty text after newsflash is over
        """
        self.news_label.text = ''

    def flash_news(self, text):
        """
        display a newsflash
        """
        counter = 0
        text = min(3 * len(text), 700) * ' ' + text
        counter_end = int(len(text) * 0.75)
        while counter < counter_end and self.news_status:
            self.news_label.text = text
            text = text[1:] + ' '
            counter += 1
            sleep(0.02)
        self.reset_news_label()

    def set_display_mode(self, instance, load_up=False):
        """
        sets 0 for dark mode, 1 for light mode
        """

        if not load_up:
            self.current_display_mode = 0 if self.current_display_mode else 1

        self.button_display_mode.text = self.display_mode_mapping[self.current_display_mode]

        with self.main_layout.canvas.before:

            if self.current_display_mode == 1:
                Color(self._LIGHT_MODE_RGB)
                self.button_refresh.background_normal = 'icons/light_mode/refresh_icon_light.png'
                self.button_refresh.background_down = 'icons/light_mode/refresh_icon_light.png'
                self.button_settings.background_normal = 'icons/light_mode/settings_icon_light.png'
                self.button_settings.background_down = 'icons/light_mode/settings_icon_light.png'
                Rectangle(size=(9999, 9999))
            else:
                Color(self._DARK_MODE_RGB)
                self.button_refresh.background_normal = 'icons/dark_mode/refresh_icon_dark.png'
                self.button_refresh.background_down = 'icons/dark_mode/refresh_icon_dark.png'
                self.button_settings.background_normal = 'icons/dark_mode/settings_icon_dark.png'
                self.button_settings.background_down = 'icons/dark_mode/settings_icon_dark.png'
                self.main_layout.canvas.before.clear()

        self.entry_price_label.color = self._TEXT_COLOR_LIGHTMODE if self.current_display_mode else \
            self._TEXT_COLOR_DARKMODE
        self.news_label.color = self._TEXT_COLOR_LIGHTMODE if self.current_display_mode else \
            self._TEXT_COLOR_DARKMODE

        if self.pnl_label.text == self.zero_pnl:  # if zero pnl
            self.pnl_label.color = self._TEXT_COLOR_LIGHTMODE if self.current_display_mode else \
                self._TEXT_COLOR_DARKMODE
        self.update_cum_pnl_label()
        self.update_position_label()

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
        self.stop_ticker(self.current_symbol)
        self.reset_pnl()
        self.reset_position()

        self.current_symbol = new_symbol
        self.update_symbol_label()
        self.start_ticker(new_symbol)
        self.main_symbol_button.text = new_symbol

    def on_press_news(self, instance):
        """
        enable / disable newsflash
        """
        self.news_status = not self.news_status
        if not self.news_status:
            self.news_fetcher.turn_off()
        self.button_news.text = self.generate_news_button_text()
        if self.news_status:
            self.start_news_flasher()

    def generate_news_button_text(self):
        """
        generate label for news toggler based on status
        """
        return f'Display news - {self.news_status}'

    def update_fees_label(self):
        """
        update fees button label
        """
        self.user_fees = round(self.user_fees, 2)
        self.fees_label.text = f"{self.user_fees}"

    def on_press_fees(self, instance):
        """
        Open `about` popup window
        """
        self.fees_window.open()

    def on_press_fees_up(self, instance):
        """
        increments fees and updates label
        """
        self.user_fees += 0.01
        self.update_fees_label()

    def on_press_fees_down(self, instance):
        """
        decrements fees and updates label
        """
        self.user_fees -= 0.01
        self.update_fees_label()

    def on_press_about(self, instance):
        """
        Open `fees` popup window
        """
        self.about_window.open()

    @staticmethod
    def on_ref_press(*args):
        """
        open ref link
        """
        webbrowser.open(args[1])

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

    def apply_fees(self):
        """
        apply fees to pnl
        """
        self.current_pnl -= self.user_fees

    def reset_cum_pnl(self):
        """
        resets cumulative pnl
        """
        self.cumulative_pnl = self._DEF_CUM_PNL
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
        * updates cumulative pnl (with fees)
        * resets position status
        * resets entry price
        * resets pos pnl
        """
        self.cumulative_pnl += (self.current_pnl - self.user_fees)
        self.current_position = 0
        self.entry_price = 0
        self.reset_pnl()
        self.update_position_label()
        self.update_entry_label()

    def reset_pnl(self):
        """Reset pnl label"""
        self.pnl_label.text = self.zero_pnl
        self.pnl_label.color = self._TEXT_COLOR_LIGHTMODE if self.current_display_mode else self._TEXT_COLOR_DARKMODE

    def on_price_update(self, price):
        """
        will be passed as callback to ws stream
        """
        self.update_pnl(price)
        precision = self.price_fetcher.get_symbol_precision(self.current_symbol)
        self.price_label.text = f'{price:.{precision}f}'
        if price > self.last_price:
            self.price_label.color = get_color_from_hex(self._GREEN_HEX)
        else:
            self.price_label.color = get_color_from_hex(self._RED_HEX)

        self.last_price = price

    def update_pnl(self, price):
        """
        calculates current position PnL and updates the label accordingly
        takes user fees into account
        """
        if self.current_position != 0:
            self.current_pnl = (self.entry_price / price)
            self.current_pnl = (self.current_pnl - 1) * 100 if self.current_position == -1 else \
                (1 - self.current_pnl) * 100
            self.apply_fees()

            self.pnl_label.text = f'{self.current_pnl:.{self._PNL_PERC}f}%'
            if self.current_pnl > 0:
                self.pnl_label.color = get_color_from_hex(self._GREEN_HEX)
            elif self.current_pnl < 0:
                self.pnl_label.color = get_color_from_hex(self._RED_HEX)
            else:
                self.reset_pnl()

    def update_symbol_label(self):
        """
        Updates the entry price label
        """
        self.symbol_label.text = self.current_symbol

    def update_entry_label(self):
        """
        Updates the entry price label
        """
        precision = self.price_fetcher.get_symbol_precision(self.current_symbol)
        self.entry_price_label.text = f'{self.entry_price:.{precision}f}'

    def update_position_label(self):
        """
        Updates current position label
        """
        self.pos_str_label.text = self.position_mapping[self.current_position]
        if self.current_position > 0:
            self.pos_str_label.color = get_color_from_hex(self._GREEN_HEX)
        elif self.current_position < 0:
            self.pos_str_label.color = get_color_from_hex(self._RED_HEX)
        else:
            self.pos_str_label.color = self._TEXT_COLOR_LIGHTMODE if self.current_display_mode else \
                self._TEXT_COLOR_DARKMODE

    def update_cum_pnl_label(self):
        """
        Updates cumulative PNL label
        """
        self.cum_pnl_label.text = f"{round(self.cumulative_pnl, 2)}%"
        if self.cumulative_pnl > 0:
            self.cum_pnl_label.color = get_color_from_hex(self._GREEN_HEX)
        elif self.cumulative_pnl < 0:
            self.cum_pnl_label.color = get_color_from_hex(self._RED_HEX)
        else:
            self.cum_pnl_label.color = self._TEXT_COLOR_LIGHTMODE if self.current_display_mode \
                else self._TEXT_COLOR_DARKMODE
        self.save_user_data()


if __name__ == "__main__":
    app = MainApp()
    app.run()
