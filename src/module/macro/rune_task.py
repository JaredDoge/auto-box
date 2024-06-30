import asyncio
import time

import cv2
import keyboard
import mss
import numpy as np
from PIL import Image

from src import config
from src.module import util, cv2_util
from src.module.log import log
from src.module.task_executor import TaskWrapper, Looper
from src.module.template import MM_TL_TEMPLATE, MM_BR_TEMPLATE, PT_WIDTH, PT_HEIGHT, RUNE_RANGES, RUNE_TEMPLATE, \
    PLAYER_TEMPLATE

# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9


class RuneTaskWrapper(TaskWrapper):

    @staticmethod
    def task_name() -> str:
        return 'rune'

    def __init__(self):
        self.sct = None
        self.tool = config.window_tool

    def screenshot(self, window, delay=1):
        try:
            return np.array(self.sct.grab(window))
        except mss.exception.ScreenShotError:
            time.sleep(delay)

    async def _run(self):
        try:
            while True:
                # 定位遊戲
                position = self.tool.get_position()

                with mss.mss() as self.sct:
                    log('截圖')
                    self.frame = self.screenshot(position)
                if self.frame is None:
                    continue

                tl, _ = cv2_util.single_match(self.frame, MM_TL_TEMPLATE)
                _, br = cv2_util.single_match(self.frame, MM_BR_TEMPLATE)

                print(tl, br)
                mm_tl = (
                    tl[0] + MINIMAP_BOTTOM_BORDER,
                    tl[1] + MINIMAP_TOP_BORDER
                )
                mm_br = (
                    max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
                    max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
                )


                minimap = self.frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]
                filtered = cv2_util.filter_color(minimap, RUNE_RANGES)

                matches = cv2_util.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)

                player = cv2_util.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)

                if player and matches:
                    rune_pos = (matches[0][0], matches[0][1])
                    player_pos = player[0]

                    if player_pos[0] > rune_pos[0]:
                        print('人在輪的右邊')
                        keyboard.press('left')
                        await asyncio.sleep(0.1)
                        keyboard.release('left')
                    elif player_pos[0] < rune_pos[0]:
                        print('人在輪的左邊')
                        keyboard.press('right')
                        await asyncio.sleep(0.1)
                        keyboard.release('right')
                    elif player_pos[1] > rune_pos[1]:
                        print('人在輪下面')
                        keyboard.press('e')
                        await asyncio.sleep(0.05)
                        keyboard.release('e')
                        await asyncio.sleep(1)
                    elif player_pos[1] < rune_pos[1]:
                        print('人在輪上面')
                        keyboard.press('down+alt')
                        await asyncio.sleep(0.05)
                        keyboard.release('down+alt')
                    else:
                        print('到了')
                elif player:
                    print('沒找到倫')
                else:
                    print('沒找到人')

                await asyncio.sleep(0.1)

                # cv2.rectangle(self.frame, mm_tl, mm_br, (0, 255, 0), 2)

        except Exception as e:
            print(e)

    def get_task(self) -> asyncio.Task:
        return asyncio.create_task(self._run())

    def show_frame(self, frame):
        if frame is not None:
            # 将mss Screenshot对象转换为NumPy数组
            # img = np.array(self.frame)
            #
            # # 转换BGRA到BGR
            # img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

            # 使用OpenCV显示图像
            cv2.imshow('Screenshot', frame)
            cv2.waitKey(0)  # 等待按键输入
            cv2.destroyAllWindows()  # 关闭所有窗口
        else:
            print("No frame to display")

    def single_match(self, frame, template):
        """
        Finds the best match within FRAME.
        :param frame:       The image in which to search for TEMPLATE.
        :param template:    The template to match with.
        :return:            The top-left and bottom-right positions of the best match.
        """

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF)
        _, _, _, top_left = cv2.minMaxLoc(result)
        w, h = template.shape[::-1]
        bottom_right = (top_left[0] + w, top_left[1] + h)
        return top_left, bottom_right
