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

PLAYER_RANGES = (
    ((24, 186, 205), (29, 212, 255)),
)
player_filtered = cv2_util.filter_color(cv2.imread('res/min_map/player_template2.png'), PLAYER_RANGES)
PLAYER_TEMPLATE_2 = cv2.cvtColor(player_filtered, cv2.COLOR_BGR2GRAY)

PLAYER_TEMPLATE = cv2.imread('res/min_map/player_template.png', 0)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape

RUNE_BUFF_TEMPLATE = cv2.imread('res/min_map/rune_buff_template.jpg', 0)

RUNE_LOCK_BUFF_TEMPLATE_P1 = cv2.imread('res/min_map/rune_lock_buff_p1.png', 0)
RUNE_LOCK_BUFF_TEMPLATE_P2 = cv2.imread('res/min_map/rune_lock_buff_p2.png', 0)

RUNE_RANGES = (
    ((141, 148, 245), (146, 158, 255)),
)
rune_filtered = cv2_util.filter_color(cv2.imread('res/min_map/rune_template.png'), RUNE_RANGES)
RUNE_TEMPLATE = cv2.cvtColor(rune_filtered, cv2.COLOR_BGR2GRAY)

BAG_SPECIAL_SELECT_TAG_TEMPLATE = cv2.imread('res/bag_special_select_tag.png')
BAG_RIGHT_BOTTOM_TEMPLATE = cv2.imread('res/bag_right_bottom.png')
BAG_EQUIPMENT_SELECT_TAG = cv2.imread('res/bag_equipment_select_tag.png')

MONSTER_TL_TEMPLATE = cv2.imread('res/monster/monster_tl_template.png', 0)
MONSTER_BR_TEMPLATE = cv2.imread('res/monster/monster_br_template.png', 0)


LAST_DAMAGE_TEMPLATE = cv2.imread('res/monster/last_damage.png')