import cv2
import numpy as np

import cv2
import numpy as np

image = cv2.imread('res/mini_map/portal_template.png')
scale_factor = 5  # 放大的倍数
image_large = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

HSV = cv2.cvtColor(image_large, cv2.COLOR_BGR2HSV)

# 放大图像
def getpos(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # 定义一个鼠标左键按下去的事件
        print(HSV[y, x])


cv2.imshow("imageHSV", HSV)
cv2.setMouseCallback("imageHSV", getpos)
cv2.waitKey(0)

def filter_color(img, ranges):
    """
    Returns a filtered copy of IMG that only contains pixels within the given RANGES.
    on the HSV scale.
    :param img:     The image to filter.
    :param ranges:  A list of tuples, each of which is a pair upper and lower HSV bounds.
    :return:        A filtered copy of IMG.
    """

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, ranges[0][0], ranges[0][1])
    for i in range(1, len(ranges)):
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, ranges[i][0], ranges[i][1]))

    # Mask the image
    color_mask = mask > 0
    result = np.zeros_like(img, np.uint8)
    result[color_mask] = img[color_mask]
    return result


yellow_lower = (24, 186, 205)
yellow_upper = (29, 212, 255)
ranges = [(yellow_lower, yellow_upper)]

# RUNE_RANGES = (
#     ((141, 148, 245), (146, 158, 255)),
# )
# rune_filtered = filter_color(cv2.imread('res/mini_map/rune_template.png'), RUNE_RANGES)
#
# cv2.imshow('Yellow Region2', rune_filtered)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# RUNE_TEMPLATE = cv2.cvtColor(rune_filtered, cv2.COLOR_BGR2GRAY)
# cv2.imshow('Yellow Region', RUNE_TEMPLATE)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# 读取图像
# img = cv2.imread('res/test_yellow.png')
# cv2.imshow('Yellow Region', img)
# # 过滤黄色
# yellow_region = filter_color(img, ranges)
#
# # 显示结果
# cv2.imshow('Yellow Region', yellow_region)
# cv2.waitKey(0)
# cv2.destroyAllWindows()