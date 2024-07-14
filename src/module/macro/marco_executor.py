import asyncio
from typing import Dict, TypedDict, Union

from src import config
from src.data.macro_model import MacroRowModel
from src.module.log import log
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.macro.monitor_task import MonitorTaskWrapper
from src.module.looper import Looper, TaskWrapper
from src.module.macro.resolve_rune_task import ResolveRuneTaskWrapper
from src.module.task_executor import TaskExecutor


class WrapperDict(TypedDict):
    srs: Union[MonitorTaskWrapper, None]


class MacroExecutor:

    def __init__(self):
        self.is_execute = False
        self.looper = config.looper
        self.executor = TaskExecutor(self.looper)

    def start(self, macro_rows: list[MacroRowModel]):
        async def _start():
            while not config.window_tool.is_foreground():
                await asyncio.sleep(1)
                config.window_tool.to_foreground()
                log('等待中')
            log('準備開始run')
            marco = MacroTaskWrapper(macro_rows)  # 打怪腳本
            rune = ResolveRuneTaskWrapper(marco)  # 解輪腳本
            monitor = MonitorTaskWrapper(self.executor, rune, marco)  # 監視器腳本

            # 執行監視器
            self.executor.execute(MonitorTaskWrapper.NAME, monitor.create())

        self.looper.run(_start())

    def stop(self):
        self.executor.cancel_all()
