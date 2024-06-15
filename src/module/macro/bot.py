import asyncio
import threading

import keyboard

from src.data.macro_model import MacroRowModel, DelayCommandModel, KeyboardCommandModel


class MacroBot:

    def __init__(self):
        self.stop_event = asyncio.Event()
        self.stop_event.set()
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self._start_loop, daemon=True)
        t.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _player(self, macro_row: MacroRowModel):
        count = macro_row.count
        while count != 0 and not self.stop_event.is_set():
            for command in macro_row.commands:
                if self.stop_event.is_set():
                    break
                if isinstance(command, DelayCommandModel):
                    print(f"delay {command.time}")
                    elapsed = 0
                    t = command.time / 1000
                    while elapsed < t:
                        if self.stop_event.is_set():
                            break
                        await asyncio.sleep(0.001)
                        elapsed += 0.001
                elif isinstance(command, KeyboardCommandModel):
                    if command.event_type == 'down':
                        keyboard.press(command.event_name)
                        print(f"down {command.event_name}")
                    elif command.event_type == 'up':
                        keyboard.release(command.event_name)
                        print(f"up {command.event_name}")
            count -= 1
            elapsed = 0
            i = macro_row.interval / 1000
            while elapsed < i:
                if self.stop_event.is_set():
                    break
                await asyncio.sleep(0.001)
                elapsed += 0.001

    async def _main(self, macro_rows: list[MacroRowModel]):
        tasks = [self._player(macro_row) for macro_row in macro_rows]
        await asyncio.gather(*tasks)

    def start(self, macro_rows: list[MacroRowModel]):
        if not self.stop_event.is_set():
            return

        self.stop_event.clear()
        asyncio.run(self._main(macro_rows))

    def stop(self):
        self.stop_event.set()
