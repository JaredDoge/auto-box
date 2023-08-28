import time
import cv2
import keyboard
import mouse

from src.module import util
import mss
import numpy as np
from src import config
from src.module.log import single, log
from src.module.template import *


def rescue(window) -> bool:

    def _screenshot(sct, delay=1):
        try:
            return np.array(sct.grab(window))
        except Exception as e:
            time.sleep(delay)
    brb_result = None
    step = 0
    while config.switch.is_open():

        with mss.mss() as sct:
            # 楓谷截圖
            frame = _screenshot(sct, window)

        if frame is None:
            continue

        if step == 0:
            brb_result = util.single_match(frame, BAG_RIGHT_BOTTOM_TEMPLATE)
            if not brb_result:
                log("找不到背包右下的擴充背包阿")
                return False
            step += 1
            continue
        if step == 1:
            log('step 1 找特殊欄')
            # 找不到就按一次tab
            if not util.match(frame, BAG_SPECIAL_SELECT_TAG_TEMPLATE):
                keyboard.send('tab')
                time.sleep(0.2)
                continue
            step += 1
            continue
        elif step == 2:
            log('step 2 找最右下那格')
            # 先找到背包右下的擴充背包 在 偏移到 最右下那格
            # 格子頂端距離圖片48px
            brb_tl, brb_rb = brb_result
            mouse.move(window['left'] + brb_tl[0] + 20, window['top'] + brb_tl[1] - 24)

            # double click
            mouse.click()
            time.sleep(0.2)
            mouse.click()

            time.sleep(0.5)

            # 確定已經在裝備欄了
            if not util.match(frame, BAG_EQUIPMENT_SELECT_TAG):
                step = 1
                time.sleep(0.1)
                continue
            step += 1
            continue
        elif step == 3:
            log('step 3 放在裝備欄最右下那格')
            time.sleep(2)
            mouse.move(window['left'] + brb_tl[0] + 20, window['top'] + brb_tl[1] - 24)
            mouse.click()

            time.sleep(0.5)

            if not util.match(frame, OK_TEMPLATE):
                step += 1
                time.sleep(0.1)
                continue
            step += 1
            continue
        elif step == 4:
            log('step 4 點OK')

            if util.match(frame, OK_TEMPLATE):
                keyboard.send('enter')
                time.sleep(0.1)
                continue
            step += 1
            continue
        elif step == 5:
            log('step 5 找附加框')
            if not util.match(frame, BOX_TEMPLATE):
                time.sleep(0.3)
                continue

            log('搶救成功，繼續洗囉')
            # 搶救成功
            return True


