import asyncio
from typing import Callable
from dataclasses import asdict

import keyboard

from src import config
from src.module import screen, cv2_util
from src.module.log import log
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.looper import TaskWrapper
from src.module.macro.macro_util import get_minimap, find_player2, find_rune_buff
from enum import Enum


class SubTaskResult(Enum):
    OK = 1
    FAIL = 2
    EFFORT = 3


class ResolveRuneTaskWrapper(TaskWrapper):
    NAME = 'resolve_rune'
    _INTERVAL = 0.02

    def generate_interleaved_offsets(self, rune):
        rune_x, rune_y = rune
        positions = [(rune_x, rune_y)]  # 首先将原始位置添加到列表中

        for offset in range(1, 3):
            # 左偏移
            positions.append((rune_x - offset, rune_y))
            # 右偏移
            positions.append((rune_x + offset, rune_y))

        return positions

    def __init__(self, macro: MacroTaskWrapper):
        self.macro = macro
        self.keys = asdict(config.data.get_rune_setting())
        # 使用繩索的次數限制，有些時候輪會剛好生在邊邊，導致繩索上拉後沒站到平台
        # 就會出現無限循環的情況
        self.rope_limit = None
        self.try_index = 10

    async def _click(self, key, sleep=0.05):
        keyboard.press(key)
        await asyncio.sleep(sleep)
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

    async def _adjust(self):
        await self._click(f'{self.keys['right']}+{self.keys['jump']}')
        await asyncio.sleep(1)

    async def _try_down(self):
        keyboard.release(self.keys['right'])
        keyboard.release(self.keys['left'])
        await self._click(self.keys['down'], sleep=2)

    async def _jump_off(self):
        keyboard.release(self.keys['right'])
        keyboard.release(self.keys['left'])
        await self._click(self.keys['jump_off'])
        await asyncio.sleep(3)

    async def _resolve(self):
        try:
            self._release_all()

            await asyncio.sleep(3)

            await self._click(self.keys['collect'])

            await asyncio.sleep(2)

            full = config.window_tool.get_geometry()

            x = full['left']
            y = full['top']
            # TODO
            rune_cut = {'left': x + 381, 'top': y + 143, 'width': 576, 'height': 228}
            cut = screen.capture_rgb(rune_cut)
            di = config.machine.predict(cut)
            log(f'推斷為:{di}')
            di = di.ljust(4, 'r')[:4]
            log(f'補正為:{di}')
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

    async def _to_rune_y(self, player_y, rune_y) -> SubTaskResult:
        if abs(player_y - rune_y) <= 2:
            return SubTaskResult.OK
        elif player_y > rune_y:
            log("上拉")
            await self._rope()
            self.rope_limit -= 1
            if self.rope_limit == 0:
                # 到限制了
                return SubTaskResult.FAIL
        elif player_y < rune_y:
            log("下跳")
            await self._jump_off()
        return SubTaskResult.EFFORT

    async def _to_rune_x(self, player_x, rune_x):
        if abs(player_x - rune_x) <= 1:
            return True
        elif player_x > rune_x:
            self._go_left()
        elif player_x < rune_x:
            self._go_right()
        return False

    async def create(self, done: Callable, rune, mm_tl, mm_br):
        try:
            try_pos = self.generate_interleaved_offsets(rune)
            self.try_index = 0

            while self.try_index < len(try_pos):
                self.rope_limit = 8
                rune_x, rune_y = try_pos[self.try_index]
                log(f'目標位置{try_pos[self.try_index]}')
                while True:
                    # 遊戲截圖
                    full = await config.window_tool.get_game_screen()
                    minimap = get_minimap(full, mm_tl, mm_br)
                    player = find_player2(minimap)

                    if not player:
                        log('找不到人物')
                        done()
                        return

                    player_x, player_y = player

                    if not await self._to_rune_x(player_x, rune_x):
                        await asyncio.sleep(self._INTERVAL)
                        continue

                    result = await self._to_rune_y(player_y, rune_y)

                    if result == SubTaskResult.FAIL:
                        log(f'解輪失敗，地圖輪位置進行微調')
                        break

                    if result == SubTaskResult.EFFORT:
                        await asyncio.sleep(self._INTERVAL)
                        continue

                    await self._resolve()

                    await asyncio.sleep(2)

                    full = await config.window_tool.get_game_screen()

                    if find_rune_buff(full):
                        log('成功解輪')
                        done()
                        return
                    log(f'解輪失敗，人物位置進行微調')
                    await self._adjust()
                    await asyncio.sleep(self._INTERVAL)

                self.try_index += 1

        except Exception as e:
            print(e)
        finally:
            self._release_all()

    def _release_all(self):
        for value in self.keys.values():
            keyboard.release(value)
