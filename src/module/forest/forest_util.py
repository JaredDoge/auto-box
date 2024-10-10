from src.module import cv2_util, template, screen
from src.module.template import PORTAL_TEMPLATE

# 1-[(139, 45)]
# 2-[(174, 37), (10, 41)]
# 3-[(57, 14), (124, 67)]
# 4-[(132, 16), (24, 54)]
# 5-[(130, 4), (15, 32)]
# 6-[(19, 9), (142, 48)]
# 7-[(45, 13)]
def find_portal(minimap):
    filtered = cv2_util.filter_color(minimap, template.PORTAL_RANGES)
    matches = cv2_util.multi_match(filtered, template.PORTAL_TEMPLATE, threshold=0.9)
    return matches

def check_pass(full):
    return cv2_util.multi_match(full, template.FOREST_PASS_TEMPLATE, threshold=0.7)
