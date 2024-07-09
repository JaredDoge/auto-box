import asyncio

from src.module import cv2_util
from src.module.log import log
from src.module.template import MM_TL_TEMPLATE, MM_BR_TEMPLATE, PT_WIDTH, PT_HEIGHT, RUNE_RANGES, RUNE_TEMPLATE, \
    PLAYER_TEMPLATE


# The distance between the top of the minimap and the top of the screen
MINIMAP_TOP_BORDER = 5

# The thickness of the other three borders of the minimap
MINIMAP_BOTTOM_BORDER = 9


async def get_minimap(frame, mm_tl, mm_br):
    return frame[mm_tl[1]:mm_br[1], mm_tl[0]:mm_br[0]]


def find_rune(minimap):
    filtered = cv2_util.filter_color(minimap, RUNE_RANGES)
    matches = cv2_util.multi_match(filtered, RUNE_TEMPLATE, threshold=0.9)
    if matches:
        # 找到地圖輪了
        return matches[0][0], matches[0][1]
    return None


async def find_minimap(frame):
    while True:
        tl, _ = cv2_util.single_match(frame, MM_TL_TEMPLATE)
        _, br = cv2_util.single_match(frame, MM_BR_TEMPLATE)

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
