import sys
import typing

from PyQt5 import QtWidgets

from src.gui.page_attr import PageAttributes
from src.gui.page_bot import PageBot
from src.gui.page_setting import PageSetting


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("auto-box")
        self.setFixedSize(400, 600)

        tab_widget = QtWidgets.QTabWidget(self)
        self.setCentralWidget(tab_widget)

        page_bot = PageBot()
        tab_widget.addTab(page_bot, "附加")

        page_attr = PageAttributes()
        tab_widget.addTab(page_attr, "屬性")

        page_setting = PageSetting()
        tab_widget.addTab(page_setting, "設定")

        # 取得 QTabBar，並設定選項卡的高度
        tab_bar = tab_widget.tabBar()
        tab_bar.setStyleSheet("""
            QTabBar::tab 
            {
             height: 30px; 
             width: 70px;
             font-size: 18px;       
            }
            """)


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

