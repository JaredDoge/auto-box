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


def show_frame(frame):
    if frame is not None:
        cv2.imshow('Screenshot', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No frame to display")
