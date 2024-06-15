from PyQt5 import QtWidgets, QtCore
from PyQt5.uic.properties import QtGui

from src.data.macro_model import MacroRowModel
from src.gui.macro.main.macro_row_edit_dialog import MacroRowEditDialog


class ListWidgetItemWidget(QtWidgets.QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)
        # layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox = QtWidgets.QCheckBox()
        self.label = QtWidgets.QLabel(text)

        # self.edit_button = QtWidgets.QPushButton()
        # self.edit_button.setIcon(QtGui.QIcon(QtGui.QPixmap("edit.png")))  # 替换成你的编辑图标路径
        # self.edit_button.setFixedSize(20, 20)
        # self.edit_button.setFlat(True)  # 移除按钮边框

        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)

        self.setLayout(layout)


class MarcoRowWidget(QtWidgets.QListWidget):

    def __init__(self, data_change):
        super().__init__()

        self.rows = None
        self.data_change = data_change

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
        context_menu = QtWidgets.QMenu(self)

        delete_action = context_menu.addAction("刪除")
        edit_action = context_menu.addAction("編輯")

        action = context_menu.exec_(self.mapToGlobal(pos))

        if action == delete_action:
            item = self.itemAt(pos)
            if item:
                self.remove_row(self.row(item))
        elif action == edit_action:
            item = self.itemAt(pos)
            if item:
                self.show_edit_dialog(self.row(item))

    def update_all(self, rows):
        self.clear()
        self.rows = rows
        if not rows:
            return
        for row in rows:
            self._add_item(row)

    def item_click_listener(self, listener):
        self.clicked.connect(listener)

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def _add_item(self, row: MacroRowModel):
        item = QtWidgets.QListWidgetItem()
        self.addItem(item)
        widget_item = ListWidgetItemWidget(row.name)
        item.setSizeHint(widget_item.sizeHint())
        self.setItemWidget(item, widget_item)

    def add_row(self, row, update=True):
        self._add_item(row)
        self.rows.append(row)
        if update:
            self.data_change()

    def remove_row(self, index, update=True):
        if index >= len(self.rows) or index < 0:
            return
        self.takeItem(index)
        del self.rows[index]
        if update:
            self.data_change()

    def edit_row(self, index, row):
        if index >= len(self.rows) or index < 0:
            return
        self.remove_row(index, False)
        self.add_row(row, False)
        self.data_change()

    def show_add_dialog(self):

        dialog = MacroRowEditDialog(MacroRowModel(name='', interval=500, count=-1, commands=[]))
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.add_row(dialog.get_result())

    def show_edit_dialog(self, index):
        if index >= len(self.rows) or index < 0:
            return

        dialog = MacroRowEditDialog(self.rows[index])
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.edit_row(index, dialog.get_result())

