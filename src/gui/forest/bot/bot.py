from typing import List

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont

from src import config
from src.gui.forest.bot.bot_step import BotStepWidget
from src.gui.macro.main.macro_row_widget import MarcoRowWidget


class BotWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.group_widget = None
        self.target_widget = None

        self.steps = config.data.get_forest_steps()

        self.init_ui()

    def init_ui(self):
        def _title_style(widget):
            font = QFont()
            font.setPointSize(14)
            widget.setFont(font)
            widget.setStyleSheet('''
                                QWidget {
                                    padding: 8px
                                }
                                ''')

        list_layout = QtWidgets.QHBoxLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)
        self.setLayout(list_layout)

        # 左邊的群組列表
        group_layout = QtWidgets.QVBoxLayout()

        self.group_widget = BotStepWidget(self._data_change)  # 帶入資料監聽器，有資料異動呼叫
        self.group_widget.item_select_changed(self._group_item_selection_changed)

        group_add = QtWidgets.QPushButton("+")
        group_add.setFixedSize(30, 30)
        group_add.setStyleSheet("font-size: 18px")
        group_add.setEnabled(False)
        group_add.clicked.connect(lambda: self.group_widget.show_add_dialog())

        group_title = QtWidgets.QLabel("群組")
        _title_style(group_title)
        group_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        group_layout.addWidget(group_title)
        group_layout.addWidget(self.group_widget, stretch=1)
        group_layout.addSpacing(20)
        group_layout.addWidget(group_add, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        group_layout.addSpacing(20)

        # 右邊的指令列表
        row_layout = QtWidgets.QVBoxLayout()
        self.target_widget = MarcoRowWidget(self._data_change)  # 帶入資料監聽器，有資料異動呼叫

        row_add = QtWidgets.QPushButton("+")
        row_add.setFixedSize(30, 30)
        row_add.setStyleSheet("font-size: 18px")
        row_add.clicked.connect(lambda: self._row_dialog())

        row_title = QtWidgets.QLabel("目標屬性")
        _title_style(row_title)
        row_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        row_layout.addWidget(row_title)
        row_layout.addWidget(self.target_widget, stretch=1)
        row_layout.addSpacing(20)
        row_layout.addWidget(row_add, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        row_layout.addSpacing(20)

        # 将两个垂直布局添加到水平布局中

        list_layout.addLayout(group_layout, stretch=1)
        list_layout.addLayout(row_layout, stretch=2)

        self.group_widget.update_all(self.steps)
        self.group_widget.setCurrentRow(0)

    def _data_change(self):
        config.data.set_forest_steps(self.steps)

    def _group_item_selection_changed(self):
        index = self.group_widget.currentRow()
        if index != -1:
            self.target_widget.update_all(self.steps[index].macros)

    def _row_dialog(self):
        if self.group_widget.currentRow() == -1:
            QtWidgets.QMessageBox.warning(self, "", "請先選擇群組")
            return

        self.target_widget.show_add_dialog()

    def get_run_list(self):
        index = self.group_widget.currentRow()
        return list(self.steps[index].targets)
