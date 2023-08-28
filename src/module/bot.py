import time
from dataclasses import dataclass
from typing import List

import cv2
import threading
import ctypes
import mss
import mss.windows
import numpy as np
import mouse
import mss.tools
import keyboard
from ctypes import wintypes

from src import config
from src.module import util
from src.module.log import log, single
from src.module.rescue import rescue
from src.module.template import *
from src.data.data import Data

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
#


@dataclass
class Target:
    attr: str
    count: int


class Bot:

    def __init__(self):
        self.ready = False
        self.target_attrs = None
        self.frame = None
        self.sct = None

        self.base = config.data.get_base()

        self.window = {}
        self.box = {}
        self.again_pos = {}

        self.thread = threading.Thread(target=self._main)
        self.thread.daemon = True

    def screenshot(self, window, delay=1):
        try:
            return np.array(self.sct.grab(window))
        except Exception as e:
            time.sleep(delay)

    def set_target_attrs(self, target):
        self.target_attrs = target

    def can_run(self):
        return config.switch.is_open() and self.target_attrs

    def _main(self):
        mss.windows.CAPTUREBLT = 0
        while True:
            self.ready = True
            if self.can_run():
                handle = user32.FindWindowW(None, self.base.app)
                user32.ShowWindow(handle, 9)
                user32.SetForegroundWindow(handle)
                rect = wintypes.RECT()
                user32.GetWindowRect(handle, ctypes.pointer(rect))
                rect = (rect.left, rect.top, rect.right, rect.bottom)
                rect = tuple(max(0, x) for x in rect)

                self.window['left'] = rect[0]
                self.window['top'] = rect[1]
                self.window['width'] = rect[2] - rect[0]
                self.window['height'] = rect[3] - rect[1]

                with mss.mss() as self.sct:
                    # 楓谷截圖
                    self.frame = self.screenshot(self.window)

                if self.frame is None:
                    continue

                # 定位附加框
                tl_result = util.single_match(self.frame, BOX_TL_TEMPLATE)
                br_result = util.single_match(self.frame, BOX_BR_TEMPLATE)
                if tl_result is None or br_result is None:
                    log('老鐵，要先開附加框阿')
                    config.switch.close()
                    continue

                tl, _ = tl_result
                _, br = br_result
                self.box['left'] = tl[0] + self.window['left']
                self.box['top'] = tl[1] + self.window['top']
                self.box['width'] = br[0] - tl[0]
                self.box['height'] = br[1] - tl[1]

                # 定位再次使用按鈕
                again = util.single_match(self.frame, AGAIN_TEMPLATE)

                if again is None:
                    log('滑鼠不要放在綠色按鈕上R')
                    config.switch.close()
                    continue

                again_tl, again_br = again
                x, y = util.get_center(AGAIN_TEMPLATE, again_tl)
                self.again_pos = (self.window['left'] + x, self.window['top'] + y)

                # 嘗試找附加框最長秒數
                attempt = 10
                with mss.mss() as self.sct:
                    while True:
                        if not self.can_run():
                            break

                        self.box_frame = self.screenshot(self.box)
                        if self.box_frame is None:
                            continue

                        if not util.match(self.box_frame, BOX_TEMPLATE):
                            log(f'找不到附加框({attempt})')
                            if attempt <= 0:
                                log('寄啦 附加框消失啦')
                                if config.data.get_setting().rescue and rescue(self.window):
                                    # 搶救成功
                                    continue
                                else:
                                    # 搶救失敗，或放棄急救
                                    config.switch.close()
                                    break
                            else:
                                attempt -= 1
                                time.sleep(1)
                                continue
                        # 清除附加框秒數
                        attempt = 10
                        if util.match(self.box_frame, OK_TEMPLATE):
                            keyboard.send('enter')
                            time.sleep(0.1)
                            continue

                        if not util.match(self.box_frame, LEGEND_TEMPLATE):
                            time.sleep(0.3)
                            continue

                        if not config.switch.is_open():
                            break
                        # 開始辨識淺能
                        lucky = False
                        single('=============Next=============')
                        for attrs in self.target_attrs:
                            lucky = self.find_target(attrs)
                            if lucky:
                                break

                        if lucky:
                            config.switch.close()
                            log(f'洗到囉，真香')
                            break
                        else:
                            mouse.move(self.again_pos[0], self.again_pos[1])  # 移到在使用一次
                            mouse.click()
                            time.sleep(0.1)
            else:
                time.sleep(0.01)

    def find_target(self, targets: List[Target]) -> bool:
        all_equal = True
        single('------------------------')
        for target in targets:
            find_count = len(util.template(self.box_frame, config.data.get_template(target.attr), self.base.threshold))
            single(f'{target.attr}:目標{target.count},找到{find_count}')
            if find_count != target.count:
                all_equal = False
        single('------------------------')
        return all_equal

    def start(self):
        self.thread.start()


