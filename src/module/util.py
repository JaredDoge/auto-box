
import cv2
import numpy as np
import time


def single_match(frame, template_, threshold=0.8):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template_, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, gray_template, cv2.TM_CCOEFF_NORMED)
    match_ = np.where(result >= threshold)
    print(match_[0].size)
    if match_[0].size <= 0:
        # 找不到匹配
        return None
    min_, max_, _, top_left = cv2.minMaxLoc(result)
    w, h = gray_template.shape[::-1]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    # 回傳的 [0] 為 x
    return top_left, bottom_right


def match(frame, template_, threshold=0.8):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template_, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, gray_template, cv2.TM_CCOEFF_NORMED)
    match_ = np.where(result >= threshold)
    return match_[0].size > 0


def get_center(template_, tl):
    _, w, h = template_.shape[::-1]
    return (tl[0] + w/2), (tl[1] + h/2)


def py_nms(dets, thresh):
    """Pure Python NMS baseline."""
    # x1、y1、x2、y2、以及score赋值
    # （x1、y1）（x2、y2）为box的左上和右下角标
    x1 = dets[:, 0]
    y1 = dets[:, 1]
    x2 = dets[:, 2]
    y2 = dets[:, 3]
    scores = dets[:, 4]

    # 每一个候选框的面积
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    # order是按照score降序排序的
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        # 计算当前概率最大矩形框与其他矩形框的相交框的坐标，会用到numpy的broadcast机制，得到的是向量
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        # 计算相交框的面积,注意矩形框不相交时w或h算出来会是负数，用0代替
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        # 计算重叠度IOU：重叠面积/（面积1+面积2-重叠面积）
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        # 找到重叠度不高于阈值的矩形框索引
        inds = np.where(ovr <= thresh)[0]
        # 将order序列更新，由于前面得到的矩形框索引要比矩形框在原order序列中的索引小1，所以要把这个1加回来
        order = order[inds + 1]
    return keep


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
