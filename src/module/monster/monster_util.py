import asyncio

from src import config
from src.module import cv2_util
from src.module.log import log
from src.module.template import MONSTER_BR_TEMPLATE,MONSTER_TL_TEMPLATE


def get_monster(full, tl,br):
    return full[tl[1]:br[1], tl[0]:br[0]]


async def find_monster():
    while True:
        # 遊戲截圖
        frame = await config.window_tool.get_game_screen()

        tl_result = cv2_util.single_match(frame, MONSTER_TL_TEMPLATE)
        br_result = cv2_util.single_match(frame, MONSTER_BR_TEMPLATE)

        if tl_result is None or br_result is None:
            log("找不到萌獸框")
            await asyncio.sleep(1)
            continue
        tl, _ = tl_result
        _, br = br_result

        return tl, br
