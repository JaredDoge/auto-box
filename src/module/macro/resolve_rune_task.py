import asyncio
from typing import Callable

import keyboard

from src import config
from src.module import screen, cv2_util
from src.module.log import log
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.looper import TaskWrapper
from src.module.macro.macro_util import get_minimap, find_player, find_rune_buff
from src.module.template import RUNE_BUFF_TEMPLATE


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
        try:
            log('開始解輪')
            self._release_all()

            await asyncio.sleep(1)

            await self._click(self.keys['collect'])

            await asyncio.sleep(2)

            full = config.window_tool.get_geometry()

            x = full['left']
            y = full['top']
            # screen.show_frame(await config.window_tool.get_game_screen())
            rune_cut = {'left': x + 381, 'top': y + 143, 'width': 576, 'height': 228}

            # (x + 381, y + 143, x + 957, y + 371)
            cut = screen.capture_rgb(rune_cut)
            # if cut.shape[2] == 4:
            #     cut = cv2.cvtColor(cut, cv2.COLOR_BGRA2BGR)
            print(f'{cut.size}')
            # screen.show_frame(cut)
            # maplehwnd = win32gui.FindWindow(None, "永恆谷")
            # position = win32gui.GetWindowRect(maplehwnd)
            # x, y, w, h = position
            # rune_cut = {'left': x, 'top': y, 'width': w, 'height': h}
            # screen.show_frame(screen.capture(rune_cut))

            #
            # # runepos = (x + 121, y + 143, x + 697, y + 371)
            # print(x, y, w, h)
            # cv2.imwrite('output.png', cut)
            #
            #
            # img = cv2.imread('output.png')
            #
            # print(f'{img.size}')

            # # screen.show_frame(cut)
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
        except Exception as e:
            print(f'{e}')

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
            return True
        elif player_x > rune_x:
            print('人在輪的右邊')
            self._go_left()
        elif player_x < rune_x:
            print('人在輪的左邊')
            self._go_right()
        return False

    async def create(self, done: Callable, rune, mm_tl, mm_br):
        try:
            rune_x, rune_y = rune
            while True:
                # 遊戲截圖
                full = await config.window_tool.get_game_screen()
                minimap = get_minimap(full, mm_tl, mm_br)
                player = find_player(minimap)

                if not player:
                    log('找不到人物')
                    # TODO
                    await asyncio.sleep(self._INTERVAL)
                    continue

                player_x, player_y = player

                if await self._to_rune_x(player_x, rune_x) and await self._to_rune_y(player_y, rune_y):
                    print('到了')
                    await self._resolve()
                    done()
                    break
                    # try_count = 10
                    # while try_count > 0:
                    #     await self._resolve()
                    #
                    #     await asyncio.sleep(2)
                    #
                    #     if find_rune_buff(full):
                    #         print('成功解輪')
                    #         done()
                    #         return
                    #
                    #     try_count -= 1
                    #
                    # print('解輪失敗')

                await asyncio.sleep(self._INTERVAL)

        except Exception as e:
            print(e)
        finally:
            self._release_all()

    def _release_all(self):
        for value in self.keys.values():
            keyboard.release(value)
