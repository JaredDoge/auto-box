from PyQt5 import QtWidgets, QtCore


class IgnoreRightButtonMenu(QtWidgets.QMenu):
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.RightButton:
            # 忽略右鍵
            event.ignore()
        else:
            # 如果是其他按钮单击，继续处理事件
            super().mousePressEvent(event)
