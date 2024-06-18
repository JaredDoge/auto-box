import sys

import keyboard
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QListView

from src import config
from src.gui.macro.scene_macro import SceneMarco


class MenuItemWidget(QtWidgets.QWidget):
    def __init__(self, text, icon_path):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

        icon_label = QtWidgets.QLabel()
        img = QtGui.QImage(icon_path)
        icon_label.setPixmap(QtGui.QPixmap.fromImage(img).scaledToHeight(40))
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        icon_label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))

        text_label = QtWidgets.QLabel(text)
        text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        text_label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))

        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        # self.setStyleSheet('''
        #                           QWidget{
        #                               background:#ff0;
        #                           }
        #                           '''
        #                    )


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

        # 创建ListWidget作为侧边栏
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.currentRowChanged.connect(self.display)
        self.list_widget.setStyleSheet("QListWidget { border: none; }")
        self.list_widget.setFixedWidth(70)
        # 创建StackedWidget作为主显示区
        self.stack_widget = QtWidgets.QStackedWidget()
        # 将ListWidget和StackedWidget添加到主布局中
        main_layout.addWidget(self.list_widget)
        main_layout.addWidget(self.stack_widget, stretch=1)

        # 添加项目到ListWidget并创建对应的页面
        self.add_list_item("巨集", "res/main_tab/tab_script.png", SceneMarco())
        # self.add_list_item("附加方塊", "res/main_tab/tab_attach_box.png", SceneAttachBox())

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

    def display(self, index):
        self.stack_widget.setCurrentIndex(index)


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
