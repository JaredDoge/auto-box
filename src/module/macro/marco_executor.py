import asyncio
import time
from typing import Dict, TypedDict, Union, Callable

from src import config
from src.data.macro_model import MacroRowModel
from src.module.log import log
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.macro.macro_util import find_minimap, get_minimap, find_rune, find_player
from src.module.macro.resolve_rune_task import ResolveRuneTaskWrapper
from src.module.task_executor import TaskExecutor


class MacroExecutor:
    _INTERVAL = 1

    def __init__(self):
        self.looper = config.looper
        self.current_task = ''
        self.main_task: asyncio.Task | None = None
        self.current_task: asyncio.Task | None = None
        self.stop_callback: Union[Callable, None] = None

    async def _cancel(self, task):
        if task is None:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def set_stop_callback(self, call):
        self.stop_callback = call

    def _notify_stop_callback(self):
        if self.stop_callback:
            self.stop_callback()

    def _macro_done(self):
        print("macro 完成")
        self.stop()

    def _resole_rune_done(self):
        self.current_task = None

    async def _run(self, macro_rows: list[MacroRowModel]):
        macro = MacroTaskWrapper(macro_rows)  # 打怪腳本
        resolve_rune = ResolveRuneTaskWrapper(macro)  # 解輪腳本

        try:
            while not config.window_tool.is_foreground():
                await asyncio.sleep(1)
                config.window_tool.to_foreground()
                log('等待遊戲視窗中')

            # 定位小地圖
            mm_tl, mm_br = await find_minimap()

            while True:
                full = await config.window_tool.get_game_screen()
                minimap = get_minimap(full, mm_tl, mm_br)

                rune = find_rune(minimap)
                player = find_player(minimap)
                if self.current_task and self.current_task.get_name() == resolve_rune.NAME:
                    await asyncio.sleep(self._INTERVAL)
                    continue
                if rune and player:
                    await self._cancel(self.current_task)
                    task = self.looper.run_task(resolve_rune.create(self._resole_rune_done, rune, mm_tl, mm_br))
                    task.set_name(resolve_rune.NAME)
                    self.current_task = task

                    await asyncio.sleep(self._INTERVAL)
                    continue

                if self.current_task and self.current_task.get_name() == macro.NAME:
                    await asyncio.sleep(self._INTERVAL)
                    continue
                await self._cancel(self.current_task)
                task = self.looper.run_task(macro.create(self._macro_done))
                task.set_name(macro.NAME)
                self.current_task = task

                await asyncio.sleep(self._INTERVAL)
                continue
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f'{e}')

    def start(self, macro_rows: list[MacroRowModel]):
        async def _start():
            self.main_task = self.looper.run_task(self._run(macro_rows))

        self.looper.run(_start())

    def stop(self):
        async def _stop():
            await self._cancel(self.current_task)
            self.current_task = None

            await self._cancel(self.main_task)
            self.main_task = None

            self._notify_stop_callback()

        self.looper.run(_stop())
