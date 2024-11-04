import asyncio
import sys
import traceback
from typing import Union, Callable

from src import config
from src.data.macro_model import MacroRowModel, MacroGroupModel
from src.module import screen
from src.module.feat.forest.forest_task import ForestTask
from src.module.feat.forest.prepare_task import PrepareTask
from src.module.log import log
from src.module.looper import TaskController


class ForestExecutor:
    _INTERVAL = 0.2

    def __init__(self):
        super().__init__()
        self.controller = TaskController()
        self.stop_callback: Union[Callable, None] = None

    def set_stop_callback(self, call):
        self.stop_callback = call

    async def _run(self, macro_groups: list[MacroGroupModel]):

        forest = ForestTask(self.controller, macro_groups[1:8])  # 副本裡腳本
        prepare = PrepareTask(self.controller)
        try:
            while not config.window_tool.is_foreground():
                await asyncio.sleep(1)
                config.window_tool.to_foreground()
                log('等待遊戲視窗中')

            while True:
                await self.controller.run_task('forest', forest.create())
                await asyncio.sleep(3)
                log('準備進入下一輪')
                await self.controller.run_task('prepare', prepare.create())
                await asyncio.sleep(2)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.stop()

    def start(self, macro_groups: list[MacroGroupModel]):
        async def _start():
            self.controller.run_task('main', self._run(macro_groups))

        self.controller.launch(_start())

    def stop(self):
        async def _stop():
            await self.controller.cancel_task()

            if self.stop_callback:
                self.stop_callback()

        self.controller.launch(_stop())
