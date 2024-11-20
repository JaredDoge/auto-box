import asyncio
import ctypes
from ctypes import wintypes
import dxcam
import numpy as np
from screeninfo import get_monitors  # 引入 screeninfo 套件來處理多螢幕

from src.module import screen

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()


class WindowTool:

    def __init__(self):
        self.current_screen_idx = None  # 用來儲存當前的螢幕索引
        self.camera = None  # 用來存儲當前的 DXCamera 實例

    def release(self):
        if self.camera:
            self.camera.release()

    def _handle(self):
        return user32.FindWindowW(None, '永恆谷')

    def is_foreground(self):
        return self._handle() == user32.GetForegroundWindow()

    def to_foreground(self):
        user32.ShowWindow(self._handle(), 9)
        user32.SetForegroundWindow(self._handle())

    def get_geometry(self):
        """獲取目標視窗在當前螢幕上的位置和尺寸。"""
        rect = wintypes.RECT()
        user32.GetWindowRect(self._handle(), ctypes.pointer(rect))
        rect = (rect.left, rect.top, rect.right, rect.bottom)
        rect = tuple(max(0, x) for x in rect)
        geometry = {'left': rect[0], 'top': rect[1], 'width': rect[2] - rect[0], 'height': rect[3] - rect[1]}

        # 使用 screeninfo 獲取螢幕資訊
        monitors = get_monitors()

        screen_idx = None

        # 遍歷所有螢幕並確定視窗所在的螢幕
        for idx, monitor in enumerate(monitors):
            # 檢查視窗是否位於此顯示器的範圍內
            if monitor.x <= geometry['left'] < monitor.x + monitor.width:
                screen_idx = idx
                break

        # 若視窗所在的螢幕發生改變，則更新攝影機
        if self.camera is None or self.current_screen_idx != screen_idx:
            if self.camera:
                self.camera.release()  # 釋放舊的 camera 實例
            # 創建新的 camera 實例
            self.camera = dxcam.create(output_idx=screen_idx, output_color="BGRA")
            self.current_screen_idx = screen_idx  # 儲存當前的螢幕索引
            print(f"更新視窗對應的攝影機：螢幕 {screen_idx}")

        # 調整幾何資訊，使其相對於當前螢幕
        monitor = monitors[screen_idx]
        geometry['left'] -= monitor.x  # 調整左邊界
        geometry['top'] -= monitor.y  # 調整上邊界

        # 回傳視窗的幾何資訊
        return geometry

    # def update_camera(self):
    #     """檢查是否需要更新 DXCamera 實例，並根據視窗的螢幕更新對應的 Camera 實例。"""
    #     # 根據視窗的幾何資訊來選擇對應的螢幕索引
    #     geometry = self.get_geometry()
    #
    #     # 使用 screeninfo 獲取螢幕資訊
    #     monitors = get_monitors()
    #
    #     screen_idx = None
    #
    #     # 遍歷所有螢幕並確定視窗所在的螢幕
    #     for idx, monitor in enumerate(monitors):
    #         # 檢查視窗是否位於此顯示器的範圍內
    #         if monitor.x <= geometry['left'] < monitor.x + monitor.width:
    #             screen_idx = idx
    #             break
    #
    #     # 若視窗所在的螢幕發生改變，則更新攝影機
    #     if self.camera is None or self.current_screen_idx != screen_idx:
    #         if self.camera:
    #             self.camera.release()  # 釋放舊的 camera 實例
    #         # 創建新的 camera 實例
    #         self.camera = dxcam.create(output_idx=screen_idx, output_color="BGR")
    #         self.current_screen_idx = screen_idx  # 儲存當前的螢幕索引
    #         print(f"更新視窗對應的攝影機：螢幕 {screen_idx}")
    #
    #     # 調整幾何資訊，使其相對於當前螢幕
    #     monitor = monitors[screen_idx]
    #     geometry['left'] -= monitor.x  # 調整左邊界
    #     geometry['top'] -= monitor.y  # 調整上邊界
    #
    #     return geometry

    def get_game_screen(self):
        return self.capture(self.get_geometry())

    def capture(self, window):
        """使用 dxcam 執行單次截圖，針對多螢幕設定對應螢幕。"""
        # 根據螢幕區域調整座標
        region = (window['left'], window['top'], window['left'] + window['width'], window['top'] + window['height'])

        # 若視窗在第二螢幕，則需確保使用正確的區域參數
        if self.camera:
            frame = self.camera.grab(region=region)
            if frame is not None:
                a = np.array(frame)
                # 可以這裡使用 screen.show_frame(a) 顯示圖片
                return a
        print('Frame capture error.')
        return None

    def xy_on_screen(self, x, y):
        geo = self.get_geometry()
        return x + geo['left'], y + geo['top']

    async def wait_game_screen(self):
        while True:
            frame = self.get_game_screen()
            if frame is None:
                await asyncio.sleep(1)
                continue
            return frame
