import asyncio
import sys
import time
import traceback
from typing import Union, Callable

from src import config
from src.data.macro_model import MacroRowModel
from src.module.log import log
from src.module.feat.macro.frame_provider import FrameProvider
from src.module.feat.macro.macro_task import MacroTaskWrapper
from src.module.feat.macro.macro_util import find_minimap, get_minimap, find_rune, find_player2, find_rune_lock_buff_p1, find_rune_lock_buff_p2
from src.module.feat.macro.resolve_rune_task import ResolveRuneTaskWrapper
from src.module import screen
from src.module.tools.mini_map import find_portal


class MacroExecutor(FrameProvider):
    def get_frame(self):
        return self.frame

    _INTERVAL = 0.2

    def __init__(self):
        self.looper = config.looper
        self.current_task = ''
        self.main_task: asyncio.Task | None = None
        self.current_task: asyncio.Task | None = None
        self.stop_callback: Union[Callable, None] = None
        self.frame = None

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

    async def _run(self, macro_rows: list[MacroRowModel]):
        def _macro_done():
            self.stop()

        def _resole_rune_done():
            self.current_task = None

        macro = MacroTaskWrapper(macro_rows, self)  # 打怪腳本
        resolve_rune = ResolveRuneTaskWrapper(macro)  # 解輪腳本

        try:
            while not config.window_tool.is_foreground():
                await asyncio.sleep(1)
                config.window_tool.to_foreground()
                log('等待遊戲視窗中')

            # 定位小地圖
            mm_tl, mm_br = await find_minimap()

            while True:
                full = await config.window_tool.wait_game_screen()

                if full.size <= 0:
                    log('截圖size為0')
                    await asyncio.sleep(1)
                    continue

                minimap = get_minimap(full, mm_tl, mm_br)

                if minimap.size <= 0:
                    log('小地圖size為0')
                    await asyncio.sleep(1)
                    continue

                rune = find_rune(minimap)
                player = find_player2(minimap)

                # 覆蓋每幀資料
                self.frame = {
                    'minimap': {
                        'width': mm_br[0] - mm_tl[0],
                        'height': mm_br[1] - mm_tl[1],
                        'full': minimap,
                        'rune': rune,
                        'player': player
                    }
                }

                if self.current_task and self.current_task.get_name() == resolve_rune.NAME:
                    await asyncio.sleep(self._INTERVAL)
                    continue

                if rune and player and not find_rune_lock_buff_p1(full) and not find_rune_lock_buff_p2(full):
                    await self._cancel(self.current_task)
                    task = self.looper.run_task(resolve_rune.create(_resole_rune_done, rune, mm_tl, mm_br))
                    task.set_name(resolve_rune.NAME)
                    self.current_task = task

                    await asyncio.sleep(self._INTERVAL)
                    continue

                if self.current_task and self.current_task.get_name() == macro.NAME:
                    await asyncio.sleep(self._INTERVAL)
                    continue

                await self._cancel(self.current_task)
                task = self.looper.run_task(macro.create(_macro_done))
                task.set_name(macro.NAME)
                self.current_task = task

                await asyncio.sleep(self._INTERVAL)
                continue
        except asyncio.CancelledError:
            pass
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.stop()

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

            if self.stop_callback:
                self.stop_callback()

        self.looper.run(_stop())
