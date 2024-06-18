import asyncio
import ctypes
import threading

import keyboard
from pygetwindow import getWindowsWithTitle

from src.data.macro_model import MacroRowModel, DelayCommandModel, KeyboardCommandModel

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
handle = user32.FindWindowW(None, '菇菇谷')

class MacroBot:
    sleep_interval = 0.01  # 精確到10毫秒

    def __init__(self):
        self.stop_event = asyncio.Event()
        self.stop_event.set()
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self._start_loop, daemon=True)
        t.start()

        self.all_down_keys = set()

    def _prepare_all_down_keys(self, macro_rows: list):
        self.all_down_keys.clear()
        for macro_row in macro_rows:
            for command in macro_row.commands:
                if isinstance(command, KeyboardCommandModel) and command.event_type == 'down':
                    self.all_down_keys.add(command.event_name)

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _player(self, macro_row: MacroRowModel):
        count = macro_row.count
        while count != 0 and not self._should_stop():
            for command in macro_row.commands:
                if self._should_stop():
                    break
                if isinstance(command, DelayCommandModel):
                    print(f"延遲 {command.time} 秒")
                    elapsed = 0
                    t = command.time
                    while elapsed < t:
                        if self.stop_event.is_set():
                            return
                        await asyncio.sleep(self.sleep_interval)
                        elapsed += self.sleep_interval
                elif isinstance(command, KeyboardCommandModel):
                    if command.event_type == 'down':
                        keyboard.press(command.event_name)
                        print(f"按下 {command.event_name}")
                    elif command.event_type == 'up':
                        keyboard.release(command.event_name)
                        print(f"抬起 {command.event_name}")
            count -= 1
            elapsed = 0
            i = macro_row.interval
            print(f"間隔 {macro_row.interval} 秒")
            while elapsed < i:
                if self._should_stop():
                    return
                await asyncio.sleep(self.sleep_interval)
                elapsed += self.sleep_interval

    async def _main(self, macro_rows: list[MacroRowModel]):
        tasks = [self._player(macro_row) for macro_row in macro_rows]
        await asyncio.gather(*tasks)

    def start(self, macro_rows: list[MacroRowModel]):
        if not self.stop_event.is_set():
            return

        print(self._is_my_test_app_in_foreground())

        self.stop_event.clear()
        self._prepare_all_down_keys(macro_rows)
        asyncio.run_coroutine_threadsafe(self._main(macro_rows), self.loop)

    def stop(self):
        self.stop_event.set()

        for key in self.all_down_keys:
            keyboard.release(key)

    def _is_my_test_app_in_foreground(self):
        # handle = user32.FindWindowW(None, '菇菇谷')
        foreground_window = user32.GetForegroundWindow()
        return handle == foreground_window

    def _should_stop(self):
        if self.stop_event.is_set():
            return True
        if not self._is_my_test_app_in_foreground():
            print("MyTestApp has lost focus. Stopping macro...")
            self.stop()
            return True
        return False