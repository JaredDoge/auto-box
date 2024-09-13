import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QMovie

# 创建应用程序
app = QApplication(sys.argv)

# 创建 QLabel 小部件
label = QLabel()

# 创建 QMovie 对象，并加载 GIF 文件
movie = QMovie("res/run.gif")

# 将 QMovie 设置为 QLabel 的内容
label.setMovie(movie)

# 开始播放 GIF 动画
movie.start()

# 显示窗口
label.show()

# 运行应用程序事件循环
sys.exit(app.exec_())
