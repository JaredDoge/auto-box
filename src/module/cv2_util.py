import cv2
import numpy as np

from src.module import screen


def filter_color(img, ranges):
    """
    返回一個過濾後的 IMG 副本，該副本僅包含在給定 RANGES 範圍內的像素，這裡的範圍是 HSV 色彩空間中的範圍。
    :param img:     要過濾的圖像。
    :param ranges:  一個包含上下界的 HSV 範圍元組列表。
    :return:        過濾後的 IMG 副本。如果發生錯誤，返回 None。
    """
    try:
        if img is None or img.size == 0:
            raise ValueError("圖片加載失敗或為空。請檢查圖片路徑或格式。")

        # 轉換圖像到 HSV 色彩空間
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 創建初始遮罩
        mask = cv2.inRange(hsv, ranges[0][0], ranges[0][1])

        # 遍歷範圍並合併遮罩
        for i in range(1, len(ranges)):
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, ranges[i][0], ranges[i][1]))

        # 將遮罩應用於圖像
        color_mask = mask > 0
        result = np.zeros_like(img, np.uint8)
        result[color_mask] = img[color_mask]

        return result

    except cv2.error as e:
        print(f"OpenCV 錯誤: {e}")
        screen.show_frame(img)
    except Exception as e:
        print(f"一般錯誤: {e}")
        screen.show_frame(img)
    # 返回 None 表示處理失敗
    return None


def get_center(template, tl):
    # 判斷圖像是灰度還是彩色，並解包對應的值
    if len(template.shape) == 2:  # 如果是灰度圖像
        h, w = template.shape
    else:  # 如果是彩色圖像，則有 (height, width, channels)
        _, h, w = template.shape[::-1]
    return (tl[0] + w / 2), (tl[1] + h / 2)


def match(frame, template, threshold=0.8):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
    match_ = np.where(result >= threshold)
    return match_[0].size > 0


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


def single_match_with_color(frame, template, threshold=0.8):
    # 移除 frame 的 Alpha 通道，保留 RGB，因為目前的 temple 都只有 RGB 不包含透明度
    if frame.shape[2] == 4:
        frame = frame[:, :, :3]

    if frame.shape[2] != template.shape[2]:
        raise ValueError("Frame and template must have the same number of channels.")

    # 分別匹配 B, G, R 三個通道
    result_b = cv2.matchTemplate(frame[:, :, 0], template[:, :, 0], cv2.TM_CCOEFF_NORMED)
    result_g = cv2.matchTemplate(frame[:, :, 1], template[:, :, 1], cv2.TM_CCOEFF_NORMED)
    result_r = cv2.matchTemplate(frame[:, :, 2], template[:, :, 2], cv2.TM_CCOEFF_NORMED)

    # 將三個通道的匹配結果平均
    result = (result_b + result_g + result_r) / 3

    # 獲取最大匹配值
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 如果匹配值小於門檻值，返回 None
    if max_val < threshold:
        return None

    # 獲取匹配區域的左上角與右下角
    top_left = max_loc
    w, h = template.shape[1], template.shape[0]
    bottom_right = (top_left[0] + w, top_left[1] + h)

    return top_left, bottom_right


def multi_channel_match(frame, template, threshold=0.9):
    if frame.shape[2] != template.shape[2]:
        raise ValueError("Frame and template must have the same number of channels.")

    result_r = cv2.matchTemplate(frame[:, :, 0], template[:, :, 0], cv2.TM_CCOEFF_NORMED)
    result_g = cv2.matchTemplate(frame[:, :, 1], template[:, :, 1], cv2.TM_CCOEFF_NORMED)
    result_b = cv2.matchTemplate(frame[:, :, 2], template[:, :, 2], cv2.TM_CCOEFF_NORMED)

    # 平均三個通道的結果
    result = (result_r + result_g + result_b) / 3
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val < threshold:
        return None

    top_left = max_loc
    w, h = template.shape[1], template.shape[0]
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


def unique(img, template, template_threshold=0.8):
    """
    img_gray:待检测的灰度图片格式
    template_img:模板小图，也是灰度化了
    template_threshold:模板匹配的置信度
    """

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

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    template_img = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
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
