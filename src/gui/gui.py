import sys

import keyboard
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QLabel

from src import config
from src.gui.macro.scene_macro import SceneMarco
from src.gui.scene_attach_box import SceneAttachBox


class BaseItemWidget(QtWidgets.QWidget):

    def __init__(self, text, icon_path):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)
        icon_label = QtWidgets.QLabel()
        img = QtGui.QImage(icon_path)
        icon_label.setPixmap(QtGui.QPixmap.fromImage(img).scaledToHeight(30))
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        icon_label.setAttribute(Qt.Qt.WA_TranslucentBackground)

        text_label = QtWidgets.QLabel(text)
        text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        text_label.setAttribute(Qt.Qt.WA_TranslucentBackground)

        self.setAttribute(Qt.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
                        QWidget {
                            background-color: white;
                        }
                        QWidget:hover {
                            background-color: #F0F0F0;
                        }
                    """)
        layout.addWidget(icon_label)
        layout.addWidget(text_label)


class MenuItemWidget(BaseItemWidget):
    def __init__(self, text, icon_path):
        super().__init__(text, icon_path)
        self.selected_indicator = QLabel(self)
        self.selected_indicator.setGeometry(5, 5, 10, 10)  # Set the position and size of the indicator
        self.selected_indicator.setStyleSheet("background-color: red; border-radius: 5px;")  # Solid circle styling

    def set_selected(self, selected):
        self.selected_indicator.setVisible(selected)


class FeatureItemWidget(BaseItemWidget):
    def __init__(self, text, icon_path):
        super().__init__(text, icon_path)
        self.click_listener = None

    def set_click_listener(self, listener):
        self.click_listener = listener

    def mousePressEvent(self, event):
        print("Widget Clicked!")
        if self.click_listener:
            self.click_listener()
        super().mousePressEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    key_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MapleBot")
        self.setFixedSize(600, 600)

        self.is_start = False
        self.key_signal.connect(self.switch)

        # 创建一个主部件并设置布局
        container = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        menu_layout = QtWidgets.QVBoxLayout()

        # 创建ListWidget作为侧边栏
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.currentRowChanged.connect(self._on_item_selection_changed)
        self.list_widget.setStyleSheet("QListWidget { border: none; }")
        self.list_widget.setFixedWidth(70)

        self.start_btn = FeatureItemWidget("啟動(F5)", "res/play.png")
        self.setting_btn = FeatureItemWidget("設定", "res/settings.png")

        menu_layout.addWidget(self.list_widget, stretch=1)
        menu_layout.addWidget(self.start_btn)
        menu_layout.addWidget(self.setting_btn)

        # 创建StackedWidget作为主显示区
        self.stack_widget = QtWidgets.QStackedWidget()
        # 将ListWidget和StackedWidget添加到主布局中
        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.stack_widget, stretch=1)

        # 添加项目到ListWidget并创建对应的页面
        self.add_list_item("巨集", "res/main_tab/tab_script.png", SceneMarco())
        self.add_list_item("附加方塊", "res/main_tab/tab_attach_box.png", SceneAttachBox())

        keyboard.on_release_key('f4', lambda _: self.key_signal.emit())

    @pyqtSlot()
    def switch(self, _=None):
        if self.is_start:
            print('停止')
            self.is_start = False
            config.macro_bot.stop()
        else:
            self.is_start = True
            print('開始')
            groups = config.data.get_macro_groups()
            l = groups[0].macros
            config.macro_bot.start(list(filter(lambda m: m.run, l)))

    def add_list_item(self, text: str, icon_path, stack):
        self.stack_widget.addWidget(stack)

        item = QtWidgets.QListWidgetItem()
        widget = MenuItemWidget(text, icon_path)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)

    def _on_item_selection_changed(self, index):
        self.stack_widget.setCurrentIndex(index)
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            widget.set_selected(i == index)


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
