import cv2

from src.module import cv2_util

DEPEND_TL_TEMPLATE = cv2.imread('res/depend/depend_tl.png', cv2.IMREAD_GRAYSCALE)
DEPEND_BR_TEMPLATE = cv2.imread('res/depend/depend_br.png', cv2.IMREAD_GRAYSCALE)
DEPEND_TEMPLATE = cv2.imread('res/depend/depend.png', cv2.IMREAD_UNCHANGED)  # 珍貴跟恢復 要用顏色分差別
DEPEND_AGAIN_TEMPLATE = cv2.imread('res/depend/depend_again.png', cv2.IMREAD_GRAYSCALE)
DEPEND_AGAIN_DISABLE_TEMPLATE = cv2.imread('res/depend/depend_again_disable.png', cv2.IMREAD_UNCHANGED)

# RECOVER_OK_TEMPLATE = DEPEND_OK_TEMPLATE
RECOVER_TL_TEMPLATE = cv2.imread('res/depend/recover_tl.png', cv2.IMREAD_GRAYSCALE)
RECOVER_BR_TEMPLATE = cv2.imread('res/depend/recover_br.png', cv2.IMREAD_GRAYSCALE)
RECOVER_AFTER_TEMPLATE = cv2.imread('res/depend/recover_after.png', cv2.IMREAD_GRAYSCALE)
RECOVER_TEMPLATE = cv2.imread('res/depend/recover.png', cv2.IMREAD_UNCHANGED)  # 珍貴跟恢復 要用顏色分差別
RECOVER_AGAIN_TEMPLATE = cv2.imread('res/depend/recover_again.png', cv2.IMREAD_GRAYSCALE)

LEGEND_TEMPLATE = cv2.imread('res/depend/legend.png', cv2.IMREAD_UNCHANGED)  # 傳說字眼 包含RGB辨識比較準確
OK_TEMPLATE = cv2.imread('res/depend/ok.png', cv2.IMREAD_GRAYSCALE)

CHANNEL_CHANGE = cv2.imread('res/depend/rescue/channel_change.png', cv2.IMREAD_UNCHANGED)

BAG_SPECIAL_SELECT_TAG_TEMPLATE = cv2.imread('res/depend/bag/bag_special_select_tag.png', cv2.IMREAD_GRAYSCALE)
BAG_RIGHT_BOTTOM_TEMPLATE = cv2.imread('res/depend/bag/bag_right_bottom.png', cv2.IMREAD_GRAYSCALE)
BAG_EQUIPMENT_SELECT_TAG = cv2.imread('res/depend/bag/bag_equipment_select_tag.png', cv2.IMREAD_GRAYSCALE)

MM_TL_TEMPLATE = cv2.imread('res/mini_map/minimap_tl_template.png', cv2.IMREAD_GRAYSCALE)
MM_BR_TEMPLATE = cv2.imread('res/mini_map/minimap_br_template.png', cv2.IMREAD_GRAYSCALE)

PLAYER_RANGES = (
    ((24, 186, 205), (29, 212, 255)),
)
PLAYER_FILTERED = cv2_util.filter_color(cv2.imread('res/mini_map/player_template2.png'), PLAYER_RANGES)
PLAYER_TEMPLATE_2 = cv2.cvtColor(PLAYER_FILTERED, cv2.COLOR_BGR2GRAY)

PLAYER_TEMPLATE = cv2.imread('res/mini_map/player_template.png', cv2.IMREAD_GRAYSCALE)
PT_HEIGHT, PT_WIDTH = PLAYER_TEMPLATE.shape

RUNE_BUFF_TEMPLATE = cv2.imread('res/mini_map/rune_buff_template.jpg', cv2.IMREAD_GRAYSCALE)

RUNE_LOCK_BUFF_TEMPLATE_P1 = cv2.imread('res/mini_map/rune_lock_buff_p1.png', cv2.IMREAD_GRAYSCALE)
RUNE_LOCK_BUFF_TEMPLATE_P2 = cv2.imread('res/mini_map/rune_lock_buff_p2.png', cv2.IMREAD_GRAYSCALE)

RUNE_RANGES = (
    ((141, 148, 245), (146, 158, 255)),
)
RUNE_FILTERED = cv2_util.filter_color(cv2.imread('res/mini_map/rune_template.png'), RUNE_RANGES)
RUNE_TEMPLATE = cv2.cvtColor(RUNE_FILTERED, cv2.COLOR_BGR2GRAY)

PORTAL_RANGES = (
    ((96, 145, 172), (102, 237, 255)),
)
PORTAL_FILTERED = cv2_util.filter_color(cv2.imread('res/mini_map/portal_template.png'), PORTAL_RANGES)
PORTAL_TEMPLATE = cv2.cvtColor(PORTAL_FILTERED, cv2.COLOR_BGR2GRAY)


MONSTER_TL_TEMPLATE = cv2.imread('res/monster/monster_tl_template.png', cv2.IMREAD_GRAYSCALE)
MONSTER_BR_TEMPLATE = cv2.imread('res/monster/monster_br_template.png', cv2.IMREAD_GRAYSCALE)

LAST_DAMAGE_TEMPLATE = cv2.imread('res/monster/last_damage.png')

FOREST_PASS_TEMPLATE = cv2.imread('res/forest/clear.png', cv2.IMREAD_GRAYSCALE)