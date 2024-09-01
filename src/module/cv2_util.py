import cv2
import numpy as np

from src.module.util import py_nms


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


def single_match(frame, template, threshold=0.8):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        return None
    top_left = max_loc
    w, h = template.shape[::-1]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return top_left, bottom_right


def multi_match(frame, template, threshold=0.95):
    """
    Finds all matches in FRAME that are similar to TEMPLATE by at least THRESHOLD.
    :param frame:       The image in which to search.
    :param template:    The template to match with.
    :param threshold:   The minimum percentage of TEMPLATE that each result must match.
    :return:            An array of matches that exceed THRESHOLD.
    """

    if template.shape[0] > frame.shape[0] or template.shape[1] > frame.shape[1]:
        return []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    results = []
    for p in locations:
        x = int(round(p[0] + template.shape[1] / 2))
        y = int(round(p[1] + template.shape[0] / 2))
        results.append((x, y))
    return results


def template(img, template_, template_threshold=0.8):
    """
    img_gray:待检测的灰度图片格式
    template_img:模板小图，也是灰度化了
    template_threshold:模板匹配的置信度
    """
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_img = cv2.cvtColor(template_, cv2.COLOR_BGR2GRAY)
    h, w = template_img.shape[:2]
    res = cv2.matchTemplate(img_gray, template_img, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= template_threshold)  # 大于模板阈值的目标坐标
    score = res[res >= template_threshold]  # 大于模板阈值的目标置信度
    # 将模板数据坐标进行处理成左上角、右下角的格式
    xmin = np.array(loc[1])
    ymin = np.array(loc[0])
    xmax = xmin + w
    ymax = ymin + h
    xmin = xmin.reshape(-1, 1)  # 变成n行1列维度
    xmax = xmax.reshape(-1, 1)  # 变成n行1列维度
    ymax = ymax.reshape(-1, 1)  # 变成n行1列维度
    ymin = ymin.reshape(-1, 1)  # 变成n行1列维度
    score = score.reshape(-1, 1)  # 变成n行1列维度
    data_hlist = [xmin, ymin, xmax, ymax, score]
    data_hstack = np.hstack(data_hlist)  # 将xmin、ymin、xmax、yamx、scores按照列进行拼接
    thresh = 0.3  # NMS里面的IOU交互比阈值
    keep_dets = py_nms(data_hstack, thresh)
    dets = data_hstack[keep_dets]  # 最终的nms获得的矩形框
    return dets
