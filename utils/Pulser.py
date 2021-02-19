from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget


class Pulser(Widget):
    _RED = [1, 0, 0, 0.4]
    _GREEN = [0.196, 0.8, 0.196, 0.4]
    _DURATION = 1.0
    bg_color = ObjectProperty(_RED)
    size_hint = (.000001, .000001)

    def __init__(self, **kwargs):
        super(Pulser, self).__init__(**kwargs)
        red_anim = Animation(bg_color=self._RED, duration=self._DURATION)
        green_anim = Animation(bg_color=self._GREEN, duration=self._DURATION)
        self.anim = red_anim + green_anim
        self.anim.repeat = True
        self.anim.start(self)


bg_pulser = Builder.load_string('''
Pulser:
    canvas.before:
        Color:
            rgba: self.bg_color
        Rectangle:
            pos: (0, 0)
            size: (9999, 9999)

''')

