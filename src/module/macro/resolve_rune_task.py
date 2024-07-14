import asyncio
import json
import time

import cv2
import keyboard
import mss
import numpy as np
import win32gui
from PIL import Image, ImageGrab

from src import config
from src.module import cv2_util, screen
from src.module.log import log
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.looper import TaskWrapper
from src.module.macro.macro_util import get_minimap, find_player
from src.module.template import PLAYER_TEMPLATE


class ResolveRuneTaskWrapper(TaskWrapper):
    NAME = 'resolve_rune'
    _INTERVAL = 0.05

    def __init__(self, macro: MacroTaskWrapper):
        self.macro = macro

        self.keys = {'right': 'right',
                     'left': 'left',
                     'up': 'up',
                     'down': 'down',
                     'jump_off': 'down+alt',
                     'rope': 'e',
                     'collect': 'space'
                     }

    async def _click(self, key):
        keyboard.press(key)
        await asyncio.sleep(0.05)
        keyboard.release(key)

    def _go_right(self):
        keyboard.release(self.keys['left'])
        keyboard.press(self.keys['right'])

    def _go_left(self):
        keyboard.release(self.keys['right'])
        keyboard.press(self.keys['left'])

    async def _rope(self):
        keyboard.release(self.keys['right'])
        keyboard.release(self.keys['left'])
        await self._click(self.keys['rope'])
        await asyncio.sleep(3)

    async def _jump_off(self):
        keyboard.release(self.keys['right'])
        keyboard.release(self.keys['left'])
        await self._click(self.keys['jump_off'])
        await asyncio.sleep(3)

    async def _resolve(self):
        self._release_all()

        await asyncio.sleep(1)

        await self._click(self.keys['collect'])

        await asyncio.sleep(2)

        full = config.window_tool.get_geometry()

        x = full['left']
        y = full['top']
        rune_cut = {'left': x + 381, 'top': y + 143, 'width': 957, 'height': 371}
        cut = screen.capture(rune_cut)
        screen.show_frame(cut)
        di = config.machine.predict(cut)
        print(di)

        for char in di:
            if char == 'u':
                await self._click('up')
            elif char == 'd':
                await self._click('down')
            elif char == 'l':
                await self._click('left')
            elif char == 'r':
                await self._click('right')
            await asyncio.sleep(0.5)

    async def _to_rune_y(self, player_y, rune_y):
        if abs(player_y - rune_y) <= 2:
            return True
        elif player_y > rune_y:
            print('人在輪下面')
            await self._rope()
        elif player_y < rune_y:
            print('人在輪上面')
            await self._jump_off()
        return False

    async def _to_rune_x(self, player_x, rune_x):
        if abs(player_x - rune_x) <= 2:
            print('訂位到X')
            return True
        elif player_x > rune_x:
            print('人在輪的右邊')
            self._go_left()
        elif player_x < rune_x:
            print('人在輪的左邊')
            self._go_right()
        return False

    async def _run(self, rune, mm_tl, mm_br):
        try:
            rune_x, rune_y = rune
            while True:
                # 遊戲截圖
                full = await config.window_tool.get_game_screen()
                minimap = get_minimap(full, mm_tl, mm_br)
                player = find_player(minimap)

                if not player:
                    log('找不到人物')
                    await asyncio.sleep(self._INTERVAL)
                    continue

                player_x, player_y = player

                if await self._to_rune_x(player_x, rune_x) and await self._to_rune_y(player_y, rune_y):
                    print('到了')
                    await self._resolve()
                    break

                await asyncio.sleep(self._INTERVAL)


        except Exception as e:
            print(e)
        finally:
            self._release_all()

    def _release_all(self):
        for value in self.keys.values():
            keyboard.release(value)

    def create(self, rune, mm_tl, mm_br) -> asyncio.Task:
        return asyncio.create_task(self._run(rune, mm_tl, mm_br))
