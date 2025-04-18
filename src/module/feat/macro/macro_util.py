import asyncio

import cv2

from src import config
from src.module import cv2_util, screen
from src.module.log import log
from src.module.template import MM_TL_TEMPLATE, MM_BR_TEMPLATE, PT_WIDTH, PT_HEIGHT, RUNE_RANGES, RUNE_TEMPLATE, \
    PLAYER_TEMPLATE, RUNE_BUFF_TEMPLATE, PLAYER_RANGES, PLAYER_TEMPLATE_2, RUNE_LOCK_BUFF_TEMPLATE_P1, \
    RUNE_LOCK_BUFF_TEMPLATE_P2

# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9


def get_minimap(full, mm_tl, mm_br):
    return full[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]


def find_rune(minimap):
    filtered = cv2_util.filter_color(minimap, RUNE_RANGES)
    matches = cv2_util.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
    if matches:
        # 找到地圖輪了
        return matches[0][0], matches[0][1]
    return None

def get_buff_frame(full):
    # 取圖片高度的前1/4，寬度的右邊2/3部分
    return full[:full.shape[0] // 4, full.shape[1] // 3:]


def find_rune_lock_buff_p1(frame):
    return cv2_util.multi_match(frame,
                                RUNE_LOCK_BUFF_TEMPLATE_P1,
                                threshold=0.9)


def find_rune_lock_buff_p2(frame):
    return cv2_util.multi_match(frame,
                                RUNE_LOCK_BUFF_TEMPLATE_P2,
                                threshold=0.9)


def find_rune_buff(frame):
    return cv2_util.multi_match(frame,
                                RUNE_BUFF_TEMPLATE,
                                threshold=0.9)


def find_player(minimap):
    player = cv2_util.multi_match(minimap, PLAYER_TEMPLATE, threshold=0.8)
    if player:
        return player[0]
    return None


def find_player2(minimap):
    filtered = cv2_util.filter_color(minimap, PLAYER_RANGES)
    matches = cv2_util.multi_match(filtered, PLAYER_TEMPLATE_2, threshold=0.9)
    if matches:
        # 找到人物
        return matches[0][0], matches[0][1]
    return None


async def find_minimap():
    while True:
        # 遊戲截圖
        frame = await config.window_tool.wait_game_screen()

        tl, _ = cv2_util.single_match(frame, MM_TL_TEMPLATE)
        _, br = cv2_util.single_match(frame, MM_BR_TEMPLATE, 0.5)

        if tl is None or br is None:
            log("找不到小地圖")
            await asyncio.sleep(1)
            continue

        mm_tl = (
            tl[0] + MINIMAP_BOTTOM_BORDER,
            tl[1] + MINIMAP_TOP_BORDER
        )
        mm_br = (
            max(mm_tl[0] + PT_WIDTH, br[0] - MINIMAP_BOTTOM_BORDER),
            max(mm_tl[1] + PT_HEIGHT, br[1] - MINIMAP_BOTTOM_BORDER)
        )
        return mm_tl, mm_br
