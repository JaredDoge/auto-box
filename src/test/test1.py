import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class MaskWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(0, 0, 0, 150))  # 设置半透明颜色
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(self.rect())

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Overlay Example')
        self.resize(400, 300)

        # 创建主要布局
        main_layout = QtWidgets.QVBoxLayout(self)

        # 创建一个 QStackedWidget
        self.stack_widget = QtWidgets.QStackedWidget(self)
        label1 = QtWidgets.QLabel('Page 1')
        label1.setAlignment(QtCore.Qt.AlignCenter)
        label1.setStyleSheet("background-color: lightblue;")
        label2 = QtWidgets.QLabel('Page 2')
        label2.setAlignment(QtCore.Qt.AlignCenter)
        label2.setStyleSheet("background-color: lightgreen;")
        self.stack_widget.addWidget(label1)
        self.stack_widget.addWidget(label2)

        # 创建一个遮罩部件，作为 stack_widget 的子部件
        self.mask = MaskWidget(self.stack_widget)
        self.mask.resize(self.stack_widget.size())
        self.mask.hide()  # 初始隐藏遮罩

        # 添加 QStackedWidget 到布局
        main_layout.addWidget(self.stack_widget)

        # 设置布局
        self.setLayout(main_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 确保遮罩在 stack_widget 调整大小时也调整大小
        self.mask.resize(self.stack_widget.size())

    def showMask(self):
        self.mask.show()

    def hideMask(self):
        self.mask.hide()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.showMask()  # 示例：启动时显示遮罩
    sys.exit(app.exec_())
