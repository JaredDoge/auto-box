import asyncio
from typing import Dict, TypedDict, Union

from src import config
from src.data.macro_model import MacroRowModel
from src.module.log import log
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.macro.monitor_task import MonitorTaskWrapper
from src.module.looper import Looper, TaskWrapper
from src.module.task_executor import TaskExecutor

class WrapperDict(TypedDict):
    srs: Union[MonitorTaskWrapper, None]

class MacroExecutor:

    def __init__(self):
        self.is_execute = False
        self.looper = config.looper
        self.executor = TaskExecutor(self.looper)
        self.wrapper: WrapperDict = {
            'srs': None
        }


    def set(self, macro_rows: list[MacroRowModel]):
        pass
        # self.unset()
        # self.wrapper[MonitorTaskWrapper.NAME] = ()

    def unset(self):
        self.wrapper.clear()

    def start(self):
        async def _start():
            while not config.window_tool.is_foreground():
                await asyncio.sleep(1)
                config.window_tool.to_foreground()
                log('等待中')
            self.wrapper[MonitorTaskWrapper.NAME].
            self.executor.execute(MonitorTaskWrapper.NAME, )

        self.looper.run(_start())

    def stop(self):
