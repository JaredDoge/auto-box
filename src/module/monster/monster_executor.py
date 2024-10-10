import asyncio
import sys
import time
import traceback
from typing import Dict, TypedDict, Union, Callable

import cv2
import keyboard

from src import config
from src.data.macro_model import MacroRowModel
from src.module import screen, cv2_util
from src.module.log import log, single
from src.module.monster.monster_util import find_monster, get_monster
from src.module.template import LAST_DAMAGE_TEMPLATE


class MonsterExecutor:
    _INTERVAL = 1

    def __init__(self):
        self.looper = config.looper
        self.main_task: asyncio.Task | None = None
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

    async def _run(self):

        try:
            while not config.window_tool.is_foreground():
                await asyncio.sleep(1)
                config.window_tool.to_foreground()
                log('等待遊戲視窗中')

            # 定位萌獸框
            monster_tl, monster_br = await find_monster()

            while True:

                full = await config.window_tool.get_game_screen()
                monster = get_monster(full, monster_tl, monster_br)

                find_count = len(cv2_util.unique(monster, LAST_DAMAGE_TEMPLATE))
                single(f'找到{find_count}')

                if find_count >= 2:
                    keyboard.send('esc')
                    single(f'777777777 三終真香')
                    self.stop()
                    return

                keyboard.send('enter')
                await asyncio.sleep(0.2)
                keyboard.send('enter')
                await asyncio.sleep(0.8)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.stop()

    def start(self):
        async def _start():
            self.main_task = self.looper.run_task(self._run())

        self.looper.run(_start())

    def stop(self):
        async def _stop():
            await self._cancel(self.main_task)
            self.main_task = None

            if self.stop_callback:
                self.stop_callback()

        self.looper.run(_stop())
