import ctypes
import time
from ctypes import wintypes

class WindowController:
    SW_MINIMIZE = 6
    SW_RESTORE = 9

    def __init__(self, window_title):
        self.user32 = ctypes.windll.user32
        self.user32.SetProcessDPIAware()
        self.handle = self.user32.FindWindowW(None, window_title)
        if not self.handle:
            raise Exception(f"Window with title '{window_title}' not found!")

    def bring_to_front(self):
        if self.handle:
            self.user32.SetForegroundWindow(self.handle)
        else:
            print("No window handle found.")

    def minimize_window(self):
        if self.handle:
            self.user32.ShowWindow(self.handle, self.SW_MINIMIZE)
        else:
            print("No window handle found.")

    def restore_window(self):
        if self.handle:
            self.user32.ShowWindow(self.handle, self.SW_RESTORE)
        else:
            print("No window handle found.")


if __name__ == "__main__":
    window_title = '菇菇谷'  # Replace with the title of your target window
    controller = WindowController(window_title)

    # Minimize, wait, then restore and bring to front
    # controller.minimize_window()
    time.sleep(1)
    controller.restore_window()
    time.sleep(1)
    controller.bring_to_front()
