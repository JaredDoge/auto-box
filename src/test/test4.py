import cv2

# 初始化變量
drawing = False  # 是否正在畫矩形
ix, iy = -1, -1  # 起始點坐標

# 滑鼠回調函數
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, img, rect_img

    if event == cv2.EVENT_LBUTTONDOWN:
        # 按下左鍵，開始畫矩形
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        # 當移動滑鼠時，如果正在畫矩形，顯示矩形
        if drawing:
            rect_img = img.copy()  # 每次都使用原始圖片副本來避免疊加
            cv2.rectangle(rect_img, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('image', rect_img)

    elif event == cv2.EVENT_LBUTTONUP:
        # 放開左鍵，結束畫矩形並顯示範圍
        drawing = False
        rect_img = img.copy()
        cv2.rectangle(rect_img, (ix, iy), (x, y), (0, 255, 0), 2)
        cv2.imshow('image', rect_img)

        # 計算矩形的左上角坐標、寬度和高度
        x1, y1 = ix, iy
        x2, y2 = x, y
        w = abs(x2 - x1)
        h = abs(y2 - y1)

        # 顯示範圍的左上角坐標及寬高
        print(f"左上角坐標: ({x1}, {y1}), 寬度: {w}, 高度: {h}")

# 加載圖片
img = cv2.imread('123.png')
rect_img = img.copy()

# 創建一個窗口並設置滑鼠回調函數
cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_rectangle)

# 顯示圖片，等待按鍵結束
while True:
    cv2.imshow('image', rect_img)
    if cv2.waitKey(1) & 0xFF == 27:  # 按下 'Esc' 鍵退出
        break

cv2.destroyAllWindows()
