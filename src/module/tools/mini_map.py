from src.module import cv2_util, template


def find_player2(minimap):
    filtered = cv2_util.filter_color(minimap, template.PLAYER_RANGES)
    matches = cv2_util.multi_match(filtered, template.PLAYER_TEMPLATE_2, threshold=0.9)
    if matches:
        # 找到人物
        return matches[0][0], matches[0][1]
    return None


def find_portal(minimap):
    filtered = cv2_util.filter_color(minimap, template.PORTAL_RANGES)
    matches = cv2_util.multi_match(filtered, template.PORTAL_TEMPLATE, threshold=0.9)
    return matches


def find_minimap(frame):
    tl_ = cv2_util.single_match(frame, template.MM_TL_TEMPLATE)
    br_ = cv2_util.single_match(frame, template.MM_BR_TEMPLATE, 0.5)
    if tl_ is None or br_ is None:
        return None

    tl, _ = tl_
    _, br = br_

    # The distance between the top of the minimap and the top of the screen
    minimap_top_border = 5
    # The thickness of the other three borders of the minimap
    minimap_bottom_border = 9

    pt_height, pt_width = template.PLAYER_TEMPLATE.shape

    mm_tl = (
        tl[0] + minimap_bottom_border,
        tl[1] + minimap_top_border
    )
    mm_br = (
        max(mm_tl[0] + pt_width, br[0] - minimap_bottom_border),
        max(mm_tl[1] + pt_height, br[1] - minimap_bottom_border)
    )
    return mm_tl, mm_br
