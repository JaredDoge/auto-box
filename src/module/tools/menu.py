from src.module import template, cv2_util, screen


def find_menu(full):
    geo = {'left': 653, 'top': 510, 'width': 80, 'height': 54}
    cut = screen.cut_by_geometry(full, geo)
    return cv2_util.single_match(cut, template.MENU_TEMPLATE, threshold=0.7)


def _menu_geo():
    return {'left': 256, 'top': 515, 'width': 654, 'height': 287}


def find_menu_every_day(full):
    cut = screen.cut_by_geometry(full, _menu_geo())
    return cv2_util.single_match(cut, template.MENU_EVERY_DAY_TEMPLATE, threshold=0.8)


def find_menu_forest(full):
    cut = screen.cut_by_geometry(full, _menu_geo())
    return cv2_util.single_match(cut, template.MENU_FOREST_TEMPLATE, threshold=0.8)
