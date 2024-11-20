from src.module import cv2_util, template, screen
from src.module.log import log
from src.module.tools import mini_map


def get_point(level):
    """
    返回每個關卡的起點和終點座標。

    起點是角色進入關卡時的初始定點，終點則是通往下一關的傳送點位置。
    每個關卡都對應於具體的座標點 (x, y)。

    參數:
    level: int - 關卡編號

    返回值:
    list[tuple[int, int]] - 起點與終點座標（無終點的關卡只返回起點）
    """
    if level == 1:
        # 第1關: 起點 (12, 56)，終點 (139, 45)
        return [(12, 56), (139, 45)]
    elif level == 2:
        # 第2關: 起點 (10, 41)，終點 (174, 37)
        return [(10, 41), (174, 37)]
    elif level == 3:
        # 第3關: 起點 (57, 14)，終點 (124, 67)
        return [(57, 14), (124, 67)]
    elif level == 4:
        # 第4關: 起點 (24, 54)，終點 (132, 16)
        return [(24, 54), (132, 16)]
    elif level == 5:
        # 第5關: 起點 (15, 32)，終點 (130, 4)
        return [(15, 32), (130, 4)]
    elif level == 6:
        # 第6關: 起點 (19, 9)，終點 (142, 48)
        return [(19, 9), (142, 48)]
    elif level == 7:
        # 第7關: 起點 (46, 13)，無終點
        return [(46, 13)]


def get_level(frame):
    """
    根據 mini_map 返回的 portal 資料來判斷當前的關卡 level。

    portal 可能返回以下三種情況：
    1. 起點和終點座標
    2. 只有終點座標
    3. 什麼都沒返回

    根據 portal 資料與 get_point 的比對，返回對應的 level，允許座標有 ±2 的誤差範圍。

    參數:
    frame: 圖像幀數，用於從 mini_map 中找到 portal 座標

    返回值:
    int - 對應的關卡 level，若無法判斷則返回 None
    """

    def is_within_range(point1, point2, tolerance=2):
        """檢查兩個座標是否在允許的誤差範圍內，默認誤差為 ±2"""
        return abs(point1[0] - point2[0]) <= tolerance and abs(point1[1] - point2[1]) <= tolerance

    portal = mini_map.find_portal(frame)

    # 若 portal 有兩個座標點，確保 x 軸較大的為終點
    if len(portal) == 2:
        start, end = sorted(portal, key=lambda p: p[0])  # 依 x 軸進行排序，較小的為起點，較大為終點
        portal = [start, end]

    # 根據 get_point 的資料比對 portal
    for level in range(1, 8):
        points = get_point(level)
        # 比對 portal 返回的資料，首先檢查起點和終點
        if len(portal) == 2:
            if is_within_range(portal[0], points[0]) and is_within_range(portal[1], points[1]):
                return level
        # 檢查只有終點的情況
        elif len(portal) == 1:
            if is_within_range(portal[0], points[-1]):  # 比對終點
                return level
        elif level == 7:
            # 第七關沒有過關傳點，然後關卡剛進時，人物會蓋住起點
            # 所以可能會出現沒有傳點的現象
            # 這邊判斷人物是否在起點當作第七關依據
            player = mini_map.find_player2(frame)
            if player and is_within_range(player, points[0]):
                return level
    # 如果無法匹配到任何關卡，返回 None
    return None


def check_clear(full):
    if cv2_util.single_match(full, template.FOREST_CLEAR_TEMPLATE_1, threshold=0.8):
        return True
    if cv2_util.single_match(full, template.FOREST_CLEAR_TEMPLATE_2, threshold=0.8):
        return True
    if cv2_util.single_match(full, template.FOREST_CLEAR_TEMPLATE_3, threshold=0.8):
        return True
    if cv2_util.single_match(full, template.FOREST_CLEAR_TEMPLATE_4, threshold=0.8):
        return True
    if cv2_util.single_match(full, template.FOREST_CLEAR_TEMPLATE_5, threshold=0.8):
        return True
    return False


def check_failure(frame):
    return cv2_util.single_match(frame, template.FOREST_FAILURE_TEMPLATE, threshold=0.8)


def check_pass(full):
    return cv2_util.single_match(full, template.FOREST_PASS_TEMPLATE, threshold=0.9)
