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
from src.module import util, cv2_util, screen
from src.module.log import log
from src.module.macro.macro_util import find_minimap, get_minimap, find_rune
from src.module.looper import TaskWrapper, Looper
from src.module.template import MM_TL_TEMPLATE, MM_BR_TEMPLATE, PT_WIDTH, PT_HEIGHT, RUNE_RANGES, RUNE_TEMPLATE, \
    PLAYER_TEMPLATE

# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9


async def _try_find_player(position, mm_tl, mm_br):
    frame = screen.capture(position)
    if frame is None:
        await asyncio.sleep(1)
        return None
    minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
    player = cv2_util.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
    if player:
        return player[0]
    return None


async def _find_rune(mm_tl, mm_br):
    while True:
        minimap = screen.capture(screen.to_geometry(mm_tl, mm_br))

        if minimap is None:
            await asyncio.sleep(1)
            continue
        # minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
        show_frame(minimap)
        filtered = cv2_util.filter_color(minimap, RUNE_RANGES)
        matches = cv2_util.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)

        if matches:
            # 找到地圖輪了
            return matches[0][0], matches[0][1]
        await asyncio.sleep(1)


async def _min_map(tool):
    while True:
        # 定位遊戲
        geometry = tool.get_geometry()
        # 遊戲截圖
        frame = screen.capture(geometry)

        if frame is None:
            await asyncio.sleep(1)
            continue

        tl, _ = cv2_util.single_match(frame, MM_TL_TEMPLATE)
        _, br = cv2_util.single_match(frame, MM_BR_TEMPLATE)

        mm_tl = (
            tl[0] + MINIMAP_BOTTOM_BORDER,
            tl[1] + MINIMAP_TOP_BORDER
        )
        mm_br = (
            max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
            max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
        )

        return geometry, mm_tl, mm_br


async def _try_find_player(position, mm_tl, mm_br):
    frame = screen.capture(position)
    if frame is None:
        await asyncio.sleep(1)
        return None
    minimap = frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
    player = cv2_util.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
    if player:
        return player[0]
    return None


class ResolveRuneTaskWrapper(TaskWrapper):

    @staticmethod
    def task_name() -> str:
        return 'resolve_rune'

    async def _run(self):
        try:
            while True:
                # 遊戲截圖
                frame = config.window_tool.get_game_screen()
                # 找小地圖位置
                mm_tl, mm_br = find_minimap(frame)

                while True:
                    frame = config.window_tool.get_game_screen()
                    minimap = get_minimap(frame, mm_tl, mm_br)
                    # 找地圖輪
                    rune = find_rune(minimap)

                    if rune is None:
                        pass

        except Exception as e:
            print(e)
        finally:
            pass
            # keyboard.release('right')
            # keyboard.release('left')
            # keyboard.release('down+alt')
        try:
            # 找小地圖
            mm_tl, mm_br = await _min_map(self.tool)

            print(mm_tl, mm_br)
            # 找地圖輪
            rune_x, rune_y = await _find_rune(mm_tl, mm_br)

            print(f"----------------{rune_x}")
            while True:
                minimap = screen.capture(screen.to_geometry(mm_tl, mm_br))

                if minimap is None:
                    await asyncio.sleep(1)
                    continue

                player = cv2_util.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)

                if player:
                    player_x, player_y = player[0]
                    print(f'人: {player_x, player_y}  輪: {rune_x, rune_y}')

                    if abs(player_x - rune_x) <= 2:
                        print('人在輪的左右誤差範圍內')
                        if abs(player_y - rune_y) <= 2:
                            keyboard.release('right')
                            keyboard.release('left')
                            keyboard.release('down+alt')
                            print('人在輪的上下誤差範圍內')
                            print('到了')
                            await asyncio.sleep(2)
                            keyboard.press('space')
                            await asyncio.sleep(0.05)
                            keyboard.release('space')
                            await asyncio.sleep(2)
                            # 獲取窗口句柄

                            maplehwnd = win32gui.FindWindow(None, "菇菇谷")
                            position = win32gui.GetWindowRect(maplehwnd)
                            x, y, w, h = position
                            runepos = (x + 381, y + 143, x + 957, y + 371)
                            print(x, y, w, h)
                            screenshot = ImageGrab.grab(runepos, all_screens=True)

                            screenshot.save("screenshot.png")

                            img = np.array(Image.open("screenshot.png"))

                            di = config.machine.predict(img)
                            print(di)

                            async def _click(dic):
                                keyboard.press(dic)
                                await asyncio.sleep(0.1)
                                keyboard.release(dic)

                            for char in di:
                                if char == 'u':
                                    await _click('up')
                                elif char == 'd':
                                    await _click('down')
                                elif char == 'l':
                                    await _click('left')
                                elif char == 'r':
                                    await _click('right')
                                await asyncio.sleep(0.5)
                            await asyncio.sleep(5)
                        elif player_y > rune_y:
                            keyboard.release('right')
                            keyboard.release('left')
                            print('人在輪下面')
                            keyboard.press('e')
                            await asyncio.sleep(0.05)
                            keyboard.release('e')
                            await asyncio.sleep(3)
                        elif player_y < rune_y:
                            print('人在輪上面')
                            keyboard.release('right')
                            keyboard.release('left')
                            keyboard.press('down+alt')
                            await asyncio.sleep(0.05)
                            keyboard.release('down+alt')
                            await asyncio.sleep(3)
                    elif player_x > rune_x:
                        print('人在輪的右邊')
                        keyboard.release('right')
                        keyboard.press('left')
                    elif player_x < rune_x:
                        print('人在輪的左邊')
                        keyboard.release('left')
                        keyboard.press('right')

                await asyncio.sleep(0.05)
            # while True:
            #     # 定位遊戲
            #     position = self.tool.get_position()
            #     # 遊戲截圖
            #     self.frame = screen.capture(position)
            #
            #     if self.frame is None:
            #         await asyncio.sleep(1)
            #         continue
            #
            #     tl, _ = cv2_util.single_match(self.frame, MM_TL_TEMPLATE)
            #     _, br = cv2_util.single_match(self.frame, MM_BR_TEMPLATE)
            #
            #     mm_tl = (
            #         tl[0] + MINIMAP_BOTTOM_BORDER,
            #         tl[1] + MINIMAP_TOP_BORDER
            #     )
            #     mm_br = (
            #         max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
            #         max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
            #     )
            #     # 成功定位小地圖
            #     while True:
            #         minimap = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
            #         filtered = cv2_util.filter_color(minimap, RUNE_RANGES)
            #         matches = cv2_util.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
            #         if not matches:
            #             await asyncio.sleep(1)
            #             continue
            #         # 找到地圖輪了
            #         rune_pos = (matches[0][0], matches[0][1])
            #
            #         player = cv2_util.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
            #
            #         if player and matches:
            #
            #             player_pos = player[0]
            #
            #             if player_pos[0] > rune_pos[0]:
            #                 print('人在輪的右邊')
            #                 keyboard.release('right')
            #                 keyboard.press('left')
            #             elif player_pos[0] < rune_pos[0]:
            #                 print('人在輪的左邊')
            #                 keyboard.release('left')
            #                 keyboard.press('right')
            #             elif player_pos[1] > rune_pos[1]:
            #                 keyboard.release('right')
            #                 keyboard.release('left')
            #                 print('人在輪下面')
            #                 keyboard.press('e')
            #                 await asyncio.sleep(0.05)
            #                 keyboard.release('e')
            #                 await asyncio.sleep(1)
            #             elif player_pos[1] < rune_pos[1]:
            #                 print('人在輪上面')
            #                 keyboard.release('right')
            #                 keyboard.release('left')
            #                 keyboard.press('down+alt')
            #                 await asyncio.sleep(0.05)
            #                 keyboard.release('down+alt')
            #             else:
            #                 print('到了')
            #         elif player:
            #             print('沒找到倫')
            #         else:
            #             print('沒找到人')
            #
            #         await asyncio.sleep(0.1)

            # cv2.rectangle(self.frame, mm_tl, mm_br, (0, 255, 0), 2)

        except Exception as e:
            print(e)
        finally:
            keyboard.release('right')
            keyboard.release('left')
            keyboard.release('down+alt')

    def run_task(self) -> asyncio.Task:
        return asyncio.create_task(self._run())
