import asyncio
from typing import Dict

from src import config
from src.data.macro_model import MacroRowModel
from src.module.log import log
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.macro.rune_task import RuneTaskWrapper
from src.module.task_executor import Looper, TaskWrapper


class MacroExecutor:
    def _on_macro_finish(self):
        log("主動節素")

    def _on_macro_cancel(self):
        log('取消')

    def _app_to_background(self):
        log("發現不再前景了")
        self.stop()

    def __init__(self, looper: Looper):
        self.looper = looper

        self.tasks: Dict[str, asyncio.Task] = {}
        self.wrapper: Dict[str, TaskWrapper] = {}
        # self.macro = MacroTaskWrapper(macro_rows)
        # self.macro.call_back(self._on_macro_finish, self._on_macro_cancel)

        # self.window = WindowTask(self._app_to_background)

    def start(self, macro_rows: list[MacroRowModel]):
        async def _start():
            while not config.window_tool.is_foreground():
                await asyncio.sleep(1)
                config.window_tool.to_foreground()
                log('等待中')
            #
            # marco_name = MacroTaskWrapper.task_name()
            # marco_wrapper = MacroTaskWrapper(macro_rows)
            # self.wrapper[marco_name] = marco_wrapper
            # self.tasks[marco_name] = marco_wrapper.get_task()

            rune_name = RuneTaskWrapper.task_name()
            rune_wrapper = RuneTaskWrapper()
            self.wrapper[rune_name] = rune_wrapper
            self.tasks[rune_name] = rune_wrapper.get_task()

        self.looper.run(_start())

    def stop(self):
        async def _stop():
            for task in self.tasks.values():
                task.cancel()
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
            self.tasks.clear()
            print('stop')

        self.looper.run(_stop())
