import asyncio

from src.module.task_executor import TaskWrapper, Looper
from src.data.macro_model import MacroRowModel, DelayCommandModel, KeyboardCommandModel
from src.module.log import log
import keyboard


class MacroTaskWrapper(TaskWrapper):

    @staticmethod
    def task_name() -> str:
        return 'marco'

    def __init__(self, macro_rows: list[MacroRowModel], ):
        self.cancel = None
        self.finish = None
        self.macro_rows = macro_rows
        self.all_down_keys = set()

        self._prepare_all_down_keys(macro_rows)

    def call_back(self, finish, cancel):
        self.finish = finish
        self.cancel = cancel

    def _prepare_all_down_keys(self, macro_rows: list):
        self.all_down_keys.clear()
        for macro_row in macro_rows:
            for command in macro_row.commands:
                if isinstance(command, KeyboardCommandModel) and command.event_type == 'down':
                    self.all_down_keys.add(command.event_name)

    def _release_all_key(self):
        for key in self.all_down_keys:
            keyboard.release(key)

    async def _player(self, macro_row: MacroRowModel):
        count = macro_row.count

        while count != 0:
            for command in macro_row.commands:
                # if self.executor.check_stop_condition():
                #     self._release_all_key()
                #     self.executor.stop_all_task()
                #     return

                if isinstance(command, DelayCommandModel):
                    log(f"延遲 {command.time} 秒")
                    await asyncio.sleep(command.time)
                elif isinstance(command, KeyboardCommandModel):
                    if command.event_type == 'down':
                        pass
                        # keyboard.press(command.event_name)
                        # log(f"按下 {command.event_name}")
                    elif command.event_type == 'up':
                        pass
                        # keyboard.release(command.event_name)
                        # log(f"抬起 {command.event_name}")
            count -= 1
            log(f"間隔 {macro_row.interval} 秒")
            await asyncio.sleep(macro_row.interval)

    async def _run(self):
        log(f"開始執行")
        try:
            tasks = [self._player(macro_row) for macro_row in self.macro_rows]
            await asyncio.gather(*tasks)
            if self.finish:
                self.finish()
        except asyncio.CancelledError:
            if self.cancel:
                self.cancel()
        finally:
            self._release_all_key()

    def get_task(self) -> asyncio.Task:
        return asyncio.create_task(self._run())
