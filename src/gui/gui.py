import sys
from abc import ABC, abstractmethod
from typing import List

import keyboard
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QLabel

from src import config
from src.gui.macro.scene_macro import SceneMarco, SwitchListener
from src.gui.monster.scene_monster import SceneMonster
from src.gui.scene_attach_box import SceneAttachBox
from src.module.log import log
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.macro.marco_executor import MacroExecutor
from src.module.switch import SwitchState


class BaseItemWidget(QtWidgets.QWidget):

    def __init__(self, text, icon_path):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)
        self.icon_label = QtWidgets.QLabel()
        img = QtGui.QImage(icon_path)
        self.icon_label.setPixmap(QtGui.QPixmap.fromImage(img).scaledToHeight(30))
        self.icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.icon_label.setAttribute(Qt.Qt.WA_TranslucentBackground)

        self.text_label = QtWidgets.QLabel(text)
        self.text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.text_label.setAttribute(Qt.Qt.WA_TranslucentBackground)

        self.setAttribute(Qt.Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
                        QWidget {
                            background-color: white;
                        }
                        QWidget:hover {
                            background-color: #F0F0F0;
                        }
                    """)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

    def set(self, text, icon_path):
        self.text_label.setText(text)
        img = QtGui.QImage(icon_path)
        self.icon_label.setPixmap(QtGui.QPixmap.fromImage(img).scaledToHeight(30))


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
        if self.click_listener:
            self.click_listener()
        super().mousePressEvent(event)


class StackedWidget(QtWidgets.QStackedWidget):

    def __init__(self):
        super().__init__()
        # 啟動時的遮罩
        self.mask = MaskWidget(self)
        self.hide_mark()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.mask.setGeometry(self.geometry())

    def show_mark(self):
        self.mask.raise_()
        self.mask.show()

    def hide_mark(self):
        self.mask.hide()


class MaskWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)  # 遮罩不绘制系统背景

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(0, 0, 0, 150))  # 设置半透明颜色
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())  # 绘制遮罩矩形


class MainWindow(QtWidgets.QMainWindow):
    switch_state_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MapleBot")
        self.setFixedSize(600, 600)

        self.is_start = False
        self.switch_state_signal.connect(self._switch_state)
        self.resize_mask = False

        self.switch_listener: List[SwitchListener] = []

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

        self.switch_btn = FeatureItemWidget("啟動(F5)", "res/play.png")
        self.setting_btn = FeatureItemWidget("設定", "res/settings.png")

        menu_layout.addWidget(self.list_widget, stretch=1)
        menu_layout.addWidget(self.switch_btn)
        menu_layout.addWidget(self.setting_btn)

        # 创建StackedWidget作为主显示区
        self.stack_widget = QtWidgets.QStackedWidget()
        # 将ListWidget和StackedWidget添加到主布局中
        main_layout.addLayout(menu_layout)
        main_layout.addWidget(self.stack_widget, stretch=1)

        macro = SceneMarco()
        self.add_list_item("巨集", "res/main_tab/tab_script.png", macro)
        self.switch_listener.append(macro)

        monster = SceneMonster()
        self.add_list_item("萌獸", "res/main_tab/tab_monster_box.png", monster)
        self.switch_listener.append(monster)
        # 啟動鈕
        config.signal.add_listener(self._hotkey)
        self.switch_btn.set_click_listener(self._switch)

        self.mask = MaskWidget(self)
        self._hide_mask()

        config.switch.set_switch_listener(lambda state: self.switch_state_signal.emit(state))

    def _hotkey(self, event):
        if event.name == 'f4' and event.event_type == 'down':
            self._switch()

    def _switch(self):
        self.switch_listener[self.list_widget.currentRow()].switch()

    def _show_mask(self):
        if not self.resize_mask:
            self.resize_mask = True
            global_pos = self.stack_widget.mapToParent(QtCore.QPoint(0, 0))
            self.mask.resize(self.stack_widget.size())
            self.mask.move(global_pos.x(), global_pos.y())

        self.mask.show()

    def _hide_mask(self):
        self.mask.hide()

    @pyqtSlot(object)
    def _switch_state(self, state: SwitchState):
        if state == SwitchState.ON:
            self.switch_btn.setEnabled(True)
            self._show_mask()
            self.switch_btn.set("停止(F4)", "res/stop.png")
        elif state == SwitchState.OFF:
            self.switch_btn.setEnabled(True)
            self._hide_mask()
            self.switch_btn.set("啟動(F4)", "res/play.png")
        elif state == SwitchState.IDLE:
            self.switch_btn.setEnabled(False)

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
