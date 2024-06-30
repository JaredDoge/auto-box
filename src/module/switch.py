from src.module.log import log
from enum import Enum


class SwitchState(Enum):
    ON = 1
    OFF = 2
    IDLE = 0


class Switch:

    def __init__(self):
        self._state = SwitchState.OFF
        self.switch_listener = None

    def set_switch_listener(self, listener):
        self.switch_listener = listener

    def _notify(self):
        if self.switch_listener:
            self.switch_listener(self._state)

    def is_on(self):
        return self._state == SwitchState.ON

    def is_off(self):
        return self._state == SwitchState.OFF

    def on(self):
        self._state = SwitchState.ON
        self._print_state()
        self._notify()

    def off(self):
        self._state = SwitchState.OFF
        self._print_state()
        self._notify()

    def idle(self):
        self._state = SwitchState.IDLE
        self._print_state()
        self._notify()

    def _print_state(self):
        if self._state == SwitchState.ON:
            log('腳本開始')
        elif self._state == SwitchState.OFF:
            log('腳本停止')
