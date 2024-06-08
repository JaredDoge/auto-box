import sys

from PyQt5 import QtWidgets, QtCore, QtGui

from src.gui.scene_attach_box import SceneAttachBox
from src.gui.scene_script import SceneScript

class WestTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabPosition(QtWidgets.QTabWidget.West)

    def add_west_tab(self, widget, text, icon_path):

        index = self.addTab(widget, '')

        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        icon_label = QtWidgets.QLabel()
        img = QtGui.QImage(icon_path)
        icon_label.setPixmap(QtGui.QPixmap.fromImage(img).scaledToHeight(40))
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        text_label = QtWidgets.QLabel(text)
        text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(icon_label)
        layout.addWidget(text_label)

        self.tabBar().setTabButton(index, QtWidgets.QTabBar.LeftSide, tab)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MapleBot")
        self.setFixedSize(800, 600)

        main_tab_widget = WestTabWidget(self)
        self.setCentralWidget(main_tab_widget)

        main_tab_widget.add_west_tab(SceneScript(), "腳本", "res/main_tab/tab_script.png")
        main_tab_widget.add_west_tab(SceneAttachBox(), "附加方塊", "res/main_tab/tab_attach_box.png")


class GUI(QtWidgets.QApplication):
    def __init__(self, argv=None):
        if argv is None:
            argv = []
        super().__init__(argv)

        self.window = MainWindow()

    def start(self):
        self.window.show()
        sys.exit(self.exec_())

# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
#     window = MainWindow()

