from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont

from src import config
from src.data.macro_model import MacroGroupModel, MacroRowModel
from src.gui.macro.main.macro_group_widget import MarcoGroupWidget
from src.gui.macro.main.macro_row_edit_dialog import MacroRowEditDialog
from src.gui.macro.main.macro_row_widget import MarcoRowWidget


# config.data.set_tabs(self.tab_list)


class MacroMain(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.macro_group_list = config.data.get_macro_groups()

        self.group_widget = None
        self.row_widget = None

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

        self.group_widget = MarcoGroupWidget(self._data_change)  # 帶入資料監聽器，有資料異動呼叫
        self.group_widget.item_select_changed(self._group_item_selection_changed)
        self.group_widget.update_all(self.macro_group_list)
        group_add = QtWidgets.QPushButton("+")
        group_add.setFixedSize(30, 30)
        group_add.setStyleSheet("font-size: 18px")
        group_add.clicked.connect(lambda: self._group_dialog())

        group_title = QtWidgets.QLabel("群組")
        _title_style(group_title)
        group_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        # 添加部件到布局，并设置伸展因子

        group_layout.addWidget(group_title)
        group_layout.addWidget(self.group_widget, stretch=1)
        group_layout.addSpacing(20)
        group_layout.addWidget(group_add, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        group_layout.addSpacing(20)

        # 右邊的指令列表
        row_layout = QtWidgets.QVBoxLayout()
        self.row_widget = MarcoRowWidget(self._data_change)  # 帶入資料監聽器，有資料異動呼叫

        row_add = QtWidgets.QPushButton("+")
        row_add.setFixedSize(30, 30)
        row_add.setStyleSheet("font-size: 18px")
        row_add.clicked.connect(lambda: self._row_dialog())

        row_title = QtWidgets.QLabel("巨集")
        _title_style(row_title)
        row_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        row_layout.addWidget(row_title)
        row_layout.addWidget(self.row_widget, stretch=1)
        row_layout.addSpacing(20)
        row_layout.addWidget(row_add, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        row_layout.addSpacing(20)

        # 将两个垂直布局添加到水平布局中
        list_layout.addLayout(group_layout, stretch=1)
        list_layout.addLayout(row_layout, stretch=2)

        self.group_widget.setCurrentRow(0)

    def _group_item_selection_changed(self):
        index = self.group_widget.currentRow()
        if index != -1:
            self.row_widget.update_all(self.macro_group_list[index].macros)

    def get_run_list(self):
        group = self.macro_group_list[self.group_widget.currentRow()]
        # 過濾沒有打勾的腳本
        return list(filter(lambda m: m.run, group.macros))

    def _group_dialog(self):
        self.group_widget.show_add_dialog()

    # 資料有異動，更新資料庫
    def _data_change(self):
        config.data.set_macro_groups(self.macro_group_list)

    def _row_dialog(self):
        if self.group_widget.currentRow() == -1:
            QtWidgets.QMessageBox.warning(self, "", "請先選擇群組")
            return

        self.row_widget.show_add_dialog()
