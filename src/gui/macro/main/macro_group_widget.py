from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont

from src import config
from src.data.macro_model import MacroGroupModel
from src.gui.common.ignore_right_menu import IgnoreRightButtonMenu


class MarcoGroupWidget(QtWidgets.QListWidget):

    def __init__(self, data_change):
        super().__init__()
        self.groups = None
        self.data_change = data_change

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.setStyleSheet("""
                            MarcoGroupWidget {
                                border-top: 1px solid black;
                                border-bottom: 1px solid black;
                                border-left: 1px solid black;
                                border-right: none;
                                background-color: #F0F0F0;
                            }

                            MarcoGroupWidget::item:selected {
                                background-color: white;
                                color: black; 
                            }
                           """
                           )

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
            self.remove_group(self.row(item))
        elif action == edit_action:
            self.show_edit_dialog(self.row(item))

    def update_all(self, groups):
        self.clear()
        self.groups = groups
        if not groups:
            return

        for index, group in enumerate(groups):
            self._add_item(index, group)

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def _add_item(self, index, group):
        item = QtWidgets.QListWidgetItem()
        item.setText(group.name)
        font = QFont()
        font.setPointSize(14)
        item.setFont(font)
        self.insertItem(index, item)

    def add_group(self, group, index=None, update=True):
        if index is None:
            index = len(self.groups)

        self._add_item(index, group)
        self.groups.insert(index, group)
        if update:
            self.data_change()

    def remove_group(self, index, update=True):

        if index >= len(self.groups) or index < 0:
            return
        self.takeItem(index)
        del self.groups[index]

        if update:
            self.data_change()

    def edit_group(self, index, group):
        if index >= len(self.groups) or index < 0:
            return
        self.item(index).setText(group.name)
        self.data_change()

    def show_add_dialog(self):
        text, ok = QtWidgets.QInputDialog().getText(self, '', '請輸入巨集群組名稱')
        if ok:
            if len(text) == 0:
                QtWidgets.QMessageBox.warning(self, "", "群組名稱不能空白")
                return

            self.add_group(MacroGroupModel(name=text, macros=[]))

    def show_edit_dialog(self, index):
        if index >= len(self.groups) or index < 0:
            return
        group = self.groups[index]
        text, ok = QtWidgets.QInputDialog().getText(self, '', '請輸入巨集群組名稱', text=group.name)
        if ok:
            if len(text) == 0:
                QtWidgets.QMessageBox.warning(self, "", "群組名稱不能空白")
                return
            group.name = text
            self.edit_group(index, group)
