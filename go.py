import json

import numpy as np
import requests
from PIL import Image, ImageGrab

import win32gui

# 獲取窗口句柄
maplehwnd = win32gui.FindWindow(None, "菇菇谷")

position = win32gui.GetWindowRect(maplehwnd)
x, y, w, h = position
runepos = (x + 121, y + 143, x + 697, y + 371)
print(x, y, w, h)
screenshot = ImageGrab.grab(runepos, all_screens=True)

screenshot.save("screenshot.png")

img = np.array(Image.open("screenshot.png"))
sendjson = {
    'image': img.tolist()
}

r = requests.post(url="http://127.0.0.1:8001/predict", json=sendjson)
json_data = json.loads(r.text)
print(json_data['prediction'])