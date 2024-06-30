import ctypes
from ctypes import wintypes

import mss
import mss.windows

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


class WindowTool:

    def __init__(self):
        mss.windows.CAPTUREBLT = 0

    def _handle(self):
        return user32.FindWindowW(None, '菇菇谷')

    def is_foreground(self):
        return self._handle() == user32.GetForegroundWindow()

    def to_foreground(self):
        user32.ShowWindow(self._handle(), 9)
        user32.SetForegroundWindow(self._handle())

    def get_position(self):
        rect = wintypes.RECT()
        user32.GetWindowRect(self._handle(), ctypes.pointer(rect))
        rect = (rect.left, rect.top, rect.right, rect.bottom)
        rect = tuple(max(0, x) for x in rect)
        window = {'left': rect[0], 'top': rect[1], 'width': rect[2] - rect[0], 'height': rect[3] - rect[1]}
        return window
