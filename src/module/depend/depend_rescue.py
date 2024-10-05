import asyncio

import keyboard
import mouse

from src import config
from src.data.depend_model import RescueSettingModel
from src.module import cv2_util, template
from src.module.log import log


async def rescue() -> bool:
    model: RescueSettingModel = config.data.get_depend_rescue_setting()
    result = None
    step = 0
    while True:
        full = await config.window_tool.get_game_screen()

        if step == 0:
            log('step 0 開啟設定')
            if not cv2_util.single_match(full, template.CHANNEL_CHANGE):  # 找換頻選項
                keyboard.send(model.setting)  # 按下設定鍵
                await asyncio.sleep(1)
                continue
            step += 1
            continue
        elif step == 1:
            log('step 1 換頻')
            keyboard.send('enter')
            await asyncio.sleep(1)
            keyboard.send('right')  # 下個頻道
            await asyncio.sleep(1)
            keyboard.send('enter')
            step += 1
            continue
        elif step == 2:
            log('step 2 等待換頻')

            step += 1
            continue
            if not brb_result:
                log("找不到背包右下的擴充背包")
                return False
            step += 1
            continue

        if step == 0:
            log('step 0 找背包')
            brb_result = cv2_util.single_match(full, template.BAG_RIGHT_BOTTOM_TEMPLATE)
            if not brb_result:
                log("找不到背包右下的擴充背包")
                return False
            step += 1
            continue
        elif step == 1:
            log('step 1 找特殊欄')
            # 找不到就按一次tab
            if not cv2_util.match(full, template.BAG_SPECIAL_SELECT_TAG_TEMPLATE):
                keyboard.send('tab')
                await asyncio.sleep(0.2)
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

            if not util.match(frame, DEPEND_OK_TEMPLATE):
                step += 1
                time.sleep(0.1)
                continue
            step += 1
            continue
        elif step == 4:
            log('step 4 點OK')

            if util.match(frame, DEPEND_OK_TEMPLATE):
                keyboard.send('enter')
                time.sleep(0.1)
                continue
            step += 1
            continue
        elif step == 5:
            log('step 5 找附加框')
            if not util.match(frame, DEPEND_TEMPLATE):
                time.sleep(0.3)
                continue

            log('搶救成功，繼續洗囉')
            # 搶救成功
            return True
