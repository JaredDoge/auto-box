import cv2
import numpy as np


def cv_imread(path):
    cv_img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    return cv_img
