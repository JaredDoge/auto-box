import os

import cv2
import mss
import numpy as np


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
