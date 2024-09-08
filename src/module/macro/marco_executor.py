import asyncio
import time
from abc import ABC
from typing import Dict, TypedDict, Union, Callable

import cv2

from src import config
from src.data.macro_model import MacroRowModel
from src.module.log import log
from src.module.macro.frame_provider import FrameProvider
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.macro.macro_util import find_minimap, get_minimap, find_rune, find_player2, find_rune_lock_buff_p1, find_rune_lock_buff_p2
from src.module.macro.resolve_rune_task import ResolveRuneTaskWrapper


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
                full = await config.window_tool.get_game_screen()
                minimap = get_minimap(full, mm_tl, mm_br)

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


                # log(lock)
                # if lock:
                    # 获取目标位置
                    # x, y = lock[0][0], lock[0][1]

                    # # 设定矩形框的大小
                    # box_size = 50  # 矩形框的宽高，例如 50x50 像素
                    # half_size = box_size // 2
                    #
                    # # 定义矩形框的坐标
                    # top_left = (x - half_size, y - half_size)
                    # bottom_right = (x + half_size, y + half_size)
                    #
                    # # 绘制绿色矩形框
                    #
                    # cv2.rectangle(full, top_left, bottom_right, (0, 255, 0), 2)
                    #
                    # # 可选：绘制中心点标记（例如一个小圆圈）
                    # cv2.circle(full, (x, y), 5, (0, 255, 0), -1)  # -1 表示填充圆圈
                    #
                    # # 显示图像
                    # cv2.imshow('Minimap with Target', full)
                    # cv2.waitKey(0)
                    # cv2.destroyAllWindows()

                    # continue

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

            if self.stop_callback:
                self.stop_callback()

        self.looper.run(_stop())
