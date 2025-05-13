import os

from src import config
from src.module import cv2_util, screen
from src.module import template
from src.module.cv2_util import read_imread_by_path


def get_block_frame(full, block):
    tl, br = block
    return full[tl[1]:br[1], tl[0]:br[0]]


def find_depend_again_disable(frame):
    return cv2_util.single_match_with_color(frame, template.DEPEND_AGAIN_DISABLE_TEMPLATE)


def depend_exist(frame):
    return cv2_util.single_match_with_color(frame, template.DEPEND_TEMPLATE)


def find_depend_box(frame):
    tl_result = cv2_util.single_match(frame, template.DEPEND_TL_TEMPLATE)
    br_result = cv2_util.single_match(frame, template.DEPEND_BR_TEMPLATE)

    if tl_result is None or br_result is None:
        return None
    tl, _ = tl_result
    _, br = br_result

    return tl, br


def find_depend_again_center(frame):
    again = cv2_util.single_match(frame, template.DEPEND_AGAIN_TEMPLATE)
    if again is None:
        return None
    again_tl, again_br = again
    return cv2_util.get_center(template.DEPEND_AGAIN_TEMPLATE, again_tl)


def recover_exist(frame):
    return cv2_util.single_match_with_color(frame, template.RECOVER_TEMPLATE)


def find_recover_box(frame):
    tl_result = cv2_util.single_match(frame, template.RECOVER_TL_TEMPLATE)
    br_result = cv2_util.single_match(frame, template.RECOVER_BR_TEMPLATE)

    if tl_result is None or br_result is None:
        return None
    tl, _ = tl_result
    _, br = br_result

    return tl, br


def find_recover_identify_block(frame):
    tl_result = cv2_util.single_match(frame, template.RECOVER_AFTER_TEMPLATE)
    br_result = cv2_util.single_match(frame, template.RECOVER_BR_TEMPLATE)

    if tl_result is None or br_result is None:
        return None
    tl, _ = tl_result
    _, br = br_result

    return tl, br


def find_recover_again_center(frame):
    again = cv2_util.single_match(frame, template.RECOVER_AGAIN_TEMPLATE)
    if again is None:
        return None
    again_tl, again_br = again
    return cv2_util.get_center(template.RECOVER_AGAIN_TEMPLATE, again_tl)


def ok_exist(frame):
    return cv2_util.single_match(frame, template.OK_TEMPLATE)


def entry_exist(frame):
    return cv2_util.single_match_with_color(frame, template.LEGEND_TEMPLATE) or \
            cv2_util.single_match_with_color(frame, template.SCARCE_TEMPLATE) or \
            cv2_util.single_match_with_color(frame, template.RARE_TEMPLATE) or \
            cv2_util.single_match_with_color(frame, template.SPECIAL_TEMPLATE) 




def get_attr_template(attrs):
    return {a.name: read_imread_by_path(a.path) for a in attrs if os.path.exists(a.path)}
