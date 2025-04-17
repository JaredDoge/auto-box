import os
import time

import cv2
import mss
import numpy as np

class ScreenCapture:
    """螢幕擷取器類，提供單例模式的螢幕截圖功能"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ScreenCapture, cls).__new__(cls)
            cls._instance._sct = None
            cls._instance._init_capture()
        return cls._instance
    
    def _init_capture(self):
        """初始化螢幕擷取器"""
        try:
            self._sct = mss.mss()
            print("螢幕擷取器初始化成功")
        except Exception as e:
            print(f"螢幕擷取器初始化失敗: {e}")
            self._sct = None
    
    def __del__(self):
        """確保資源正確釋放"""
        if self._sct:
            self._sct.close()
            print("螢幕擷取器已釋放")
    
    def capture(self, window, rgb_only=False):
        """擷取特定視窗的螢幕畫面
        
        Args:
            window: 要擷取的視窗坐標 (left, top, width, height)
            rgb_only: 是否只返回RGB通道（不包含Alpha通道）
            
        Returns:
            numpy.ndarray 或 None: 成功時返回圖像陣列，失敗時返回None
        """
        if not self._sct:
            self._init_capture()
            if not self._sct:
                return None
                
        try:
            # 限制嘗試次數，避免無限重試
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 獲取原始圖像
                    raw_img = np.array(self._sct.grab(window))
                    
                    # 檢查是否僅需RGB通道
                    if rgb_only and len(raw_img.shape) >= 3 and raw_img.shape[2] >= 3:
                        img = raw_img[:, :, :3]  # 只保留RGB三個通道
                    else:
                        img = raw_img
                    
                    # 驗證圖像是否有效
                    if img is None or img.size == 0 or len(img.shape) < 2:
                        raise ValueError("擷取到無效的圖像")
                    return img
                    
                except mss.exception.ScreenShotError as e:
                    print(f"螢幕擷取失敗 (嘗試 {attempt+1}/{max_retries}): {e}")
                    # 短暫暫停後重試
                    time.sleep(0.2)
                    continue
                except ValueError as e:
                    print(f"圖像驗證失敗 (嘗試 {attempt+1}/{max_retries}): {e}")
                    # 短暫暫停後重試
                    time.sleep(0.2)
                    continue
                    
            print(f"多次嘗試後仍無法擷取螢幕")
            return None
        except Exception as e:
            print(f"螢幕擷取時發生未知錯誤: {e}")
            return None


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
    """與原始代碼兼容的函數，使用ScreenCapture類實現"""
    screen_capture = ScreenCapture()
    return screen_capture.capture(window)

def capture_rgb(window):
    """與原始代碼兼容的函數，使用ScreenCapture類實現，僅返回RGB通道"""
    screen_capture = ScreenCapture()
    return screen_capture.capture(window, rgb_only=True)

# def capture(window):
#     def _screenshot(s):
#         try:
#             return np.array(s.grab(window))
#         except mss.exception.ScreenShotError:
#             print('ScreenShotError.')
#             return None

#     with mss.mss() as sct:
#         return _screenshot(sct)


# def capture_rgb(window):
#     def _screenshot(s):
#         try:
#             return np.array(s.grab(window))[:, :, :3]
#         except mss.exception.ScreenShotError:
#             print('ScreenShotError.')
#             return None

#     with mss.mss() as sct:
#         return _screenshot(sct)


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
