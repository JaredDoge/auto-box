import cv2

from src.module import cv2_util

OK_TEMPLATE = cv2.imread('res/ok.png')
BOX_TL_TEMPLATE = cv2.imread('res/box_tl.png')
BOX_BR_TEMPLATE = cv2.imread('res/box_br.png')
BOX_TEMPLATE = cv2.imread('res/green_box.png')
LEGEND_TEMPLATE = cv2.imread('res/legend.png')
AGAIN_TEMPLATE = cv2.imread('res/again.png')

MM_TL_TEMPLATE = cv2.imread('res/min_map/minimap_tl_template.png', 0)
MM_BR_TEMPLATE = cv2.imread('res/min_map/minimap_br_template.png', 0)
PLAYER_TEMPLATE = cv2.imread('res/min_map/player_template.png', 0)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape

RUNE_RANGES = (
    ((141, 148, 245), (146, 158, 255)),
)
rune_filtered = cv2_util.filter_color(cv2.imread('res/min_map/rune_template.png'), RUNE_RANGES)
RUNE_TEMPLATE = cv2.cvtColor(rune_filtered, cv2.COLOR_BGR2GRAY)


BAG_SPECIAL_SELECT_TAG_TEMPLATE = cv2.imread('res/bag_special_select_tag.png')
BAG_RIGHT_BOTTOM_TEMPLATE = cv2.imread('res/bag_right_bottom.png')
BAG_EQUIPMENT_SELECT_TAG = cv2.imread('res/bag_equipment_select_tag.png')
