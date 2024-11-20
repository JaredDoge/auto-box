import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from mss import mss

class GameMonitor(QMainWindow):
    def __init__(self, monster_template_path):
        super().__init__()

        # 初始化窗口
        self.setWindowTitle("Game Monitor")
        self.setGeometry(100, 100, 1382, 807)
        self.label = QLabel(self)
        self.label.resize(1382, 807)

        # 加載怪物模板圖片並提取其特徵點
        self.monster_template = cv2.imread(monster_template_path, cv2.IMREAD_GRAYSCALE)
        self.orb = cv2.ORB_create()
        self.kp_template, self.des_template = self.orb.detectAndCompute(self.monster_template, None)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # 設置背景建模
        self.background = None
        self.background_initialized = False

        # 設置螢幕擷取區域
        self.sct = mss()
        self.monitor = {'left': 2143, 'top': 87, 'width': 1382, 'height': 807}

        # 設置計時器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        # 擷取畫面
        screenshot = self.sct.grab(self.monitor)
        frame = np.array(screenshot)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 初始化背景
        if not self.background_initialized:
            self.background = gray_frame
            self.background_initialized = True
            return

        # 背景差分
        frame_diff = cv2.absdiff(self.background, gray_frame)
        _, thresh_diff = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

        # HSV 範圍篩選
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_hsv = cv2.inRange(hsv_frame, np.array([30, 60, 60]), np.array([90, 255, 255]))
        combined_mask = cv2.bitwise_and(thresh_diff, mask_hsv)

        # 找到移動的輪廓
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            roi_gray = gray_frame[y:y + h, x:x + w]

            # ORB 特徵匹配
            kp_frame, des_frame = self.orb.detectAndCompute(roi_gray, None)
            if des_frame is not None:
                matches = self.matcher.match(self.des_template, des_frame)
                good_matches = [m for m in matches if m.distance < 60]  # 設定匹配距離門檻

                if len(good_matches) > 10:  # 足夠的匹配點數量
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # 顯示在 PyQt5 窗口
        h, w, ch = frame.shape
        qt_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)

# 啟動程式
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GameMonitor("777.png")  # 替換成怪物圖片路徑
    window.show()
    sys.exit(app.exec_())
