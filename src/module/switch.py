from PyQt5.QtCore import pyqtSignal

from src import config
from src.module.log import log


class Switch:

    def __init__(self):
        self._enabled = False
        self.switch_listener = None
        config.signal.add_listener(self._on_event)

    def _on_event(self, event):
        if event.name == 'f4':
            self.toggle()

    def set_switch_listener(self, listener):
        self.switch_listener = listener

    def _notify(self):
        if self.switch_listener:
            self.switch_listener(self.is_on())

    def is_on(self):
        return self._enabled

    def on(self):
        self._enabled = True
        self._print_state()
        self._notify()

    def off(self):
        self._enabled = False
        self._print_state()
        self._notify()

    def toggle(self, _=None):
        self._enabled = not self._enabled
        self._print_state()
        self._notify()
        # if self._enabled:
        #     winsound.Beep(784, 333)     # G5
        # else:
        #     winsound.Beep(523, 333)     # C5
        # time.sleep(0.267)

    def _print_state(self):
        if self._enabled:
            log('腳本開始')
        else:
            log('腳本停止')
