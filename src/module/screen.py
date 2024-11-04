import os

import cv2
import mss
import numpy as np


def cut_by_tl_br(full, block):
    tl, br = block
    return full[tl[1]:br[1], tl[0]:br[0]]


def cut_by_geometry(full, geometry):
    left = geometry['left']
    top = geometry['top']
    width = geometry['width']
    height = geometry['height']
    return full[top:top + height, left:left + width]


def capture(window):
    def _screenshot(s):
        try:
            return np.array(s.grab(window))
        except mss.exception.ScreenShotError:
            print('ScreenShotError.')
            return None

    with mss.mss() as sct:
        return _screenshot(sct)


def capture_rgb(window):
    def _screenshot(s):
        try:
            return np.array(s.grab(window))[:, :, :3]
        except mss.exception.ScreenShotError:
            print('ScreenShotError.')
            return None

    with mss.mss() as sct:
        return _screenshot(sct)


def show_frame(frame):
    if frame is not None:
        cv2.imshow('Screenshot', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No frame to display")


def save_frame(frame, save_path):
    cv2.imencode('.png', frame)[1].tofile(save_path)
    print(f"Frame saved to {save_path}")
