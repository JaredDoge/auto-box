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

runepos = (x + 121, y + 143, x + 697, y + 371)  # 800x600
# runepos = (x+221, y+143, x+797, y+371) # 1074x768
# runepos = (x+341, y+143, x+917, y+371) # 1280x720
# runepos = (x+381, y+143, x+957, y+371) # 1366x768
# runepos = (x+631, y+143, x+1207, y+371) # 1920x1080 # if this coordinate not work, lemme know!