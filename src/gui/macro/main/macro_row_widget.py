from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QListWidget
from PyQt5.uic.properties import QtGui

from src.data.macro_model import MacroRowModel
from src.gui.common.drag_move_qlist import DragMoveQListWidget
from src.gui.common.ignore_right_menu import IgnoreRightButtonMenu
from src.gui.macro.main.macro_row_edit_dialog import CommandSetEditDialog


class RowItemWidget(QtWidgets.QWidget):
    def __init__(self, macro: MacroRowModel, data_change):
        super().__init__()

        self.macro = macro
        self.data_change = data_change

        layout = QtWidgets.QHBoxLayout(self)

        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setChecked(macro.run)

        self.checkbox.toggled.connect(self._on_checkbox_toggled)

        info_layout = QtWidgets.QVBoxLayout()

        label_title = QtWidgets.QLabel(macro.name)
        label_title.setStyleSheet('''
                        font-size:18px;
        ''')

        label_info = QtWidgets.QLabel(self._get_info())
        label_info.setStyleSheet('''
                        font-size:14px;
                        color: #272727;
                ''')

        info_layout.addWidget(label_title)
        info_layout.addWidget(label_info)

        layout.addWidget(self.checkbox)
        layout.addSpacing(10)
        layout.addLayout(info_layout, stretch=1)

        self.setLayout(layout)

    def _get_info(self):
        count = '無限循環' if self.macro.count == -1 else f'執行 {self.macro.count} 次'
        interval = f'每次間隔 {self.macro.interval} 秒'
        return f"{count}, {interval}"

    def _on_checkbox_toggled(self, checked):
        self.macro.run = checked
        self.data_change()
        self.checkbox.setChecked(checked)


class MarcoRowWidget(DragMoveQListWidget):

    def __init__(self, data_change):
        super().__init__()

        self.rows = None
        self.data_change = data_change

        self.setSelectionMode(QListWidget.SingleSelection)

        # 连接拖放信号到槽函数
        self.model().rowsMoved.connect(self._update_data_array)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.setStyleSheet("""
                           MarcoCommandWidget {
                               border-top: 1px solid black;
                               border-bottom: 1px solid black;
                               border-left: none;
                               border-right: 1px solid black;
                           }
                           """)

    def _on_item_double_clicked(self, item):
        self.show_edit_dialog(self.row(item))

    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if item is None:
            return

        context_menu = IgnoreRightButtonMenu(self)

        edit_action = context_menu.addAction("編輯")
        delete_action = context_menu.addAction("刪除")

        action = context_menu.exec_(self.mapToGlobal(pos))

        if action == delete_action:
            self.remove_row(self.row(item))
        elif action == edit_action:
            self.show_edit_dialog(self.row(item))

    def update_all(self, rows):
        self.clear()
        self.rows = rows
        if not rows:
            return

        for index, row in enumerate(rows):
            self._add_item(index, row)

    def item_click_listener(self, listener):
        self.clicked.connect(listener)

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def _update_data_array(self, parent, start, end, destination, row):
        pop = self.rows.pop(start)
        if start > row:
            self.rows.insert(row, pop)
        else:
            self.rows.insert(row - 1, pop)
        self.data_change()

    def _add_item(self, index, row: MacroRowModel):
        item = QtWidgets.QListWidgetItem()
        self.insertItem(index, item)
        widget_item = RowItemWidget(row, self.data_change)
        item.setSizeHint(widget_item.sizeHint())
        self.setItemWidget(item, widget_item)

    def add_row(self, row, index=None, update=True):
        if index is None:
            index = len(self.rows)

        self._add_item(index, row)
        self.rows.insert(index, row)
        if update:
            self.data_change()

    def remove_row(self, index, update=True):
        if index >= len(self.rows) or index < 0:
            return
        self.takeItem(index)
        del self.rows[index]
        if update:
            self.data_change()

    def edit_row(self, index, row, focus=True):
        if index >= len(self.rows) or index < 0:
            return
        self.remove_row(index, False)
        self.add_row(row, index, False)
        if focus:
            self.setCurrentRow(index)
        self.data_change()

    def show_add_dialog(self):

        dialog = CommandSetEditDialog()
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.add_row(dialog.get_result())

    def show_edit_dialog(self, index):
        if index >= len(self.rows) or index < 0:
            return

        dialog = CommandSetEditDialog(self.rows[index])
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.edit_row(index, dialog.get_result())
