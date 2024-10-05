import os
from typing import Dict, Callable, List

from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QListWidget

from src import config
from src.data.depend_model import AttrModel
from src.gui.common.drag_move_qlist import DragMoveQListWidget, DragMoveQListWidget2
from src.gui.common.msg_box import question
from src.gui.depend.attr.attr_menu_edit import AttrMenuEditDialog


class AttrItem(QtWidgets.QWidget):
    def __init__(self, attr):
        super().__init__()

        layout = QtWidgets.QHBoxLayout(self)

        label = QtWidgets.QLabel(attr.name)
        label.setStyleSheet("font-size: 16px")
        layout.addWidget(label)

        image_label = QtWidgets.QLabel()
        if os.path.exists(attr.path):
            pixmap = QPixmap(attr.path).scaledToHeight(25)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("圖片不存在")

        layout.addWidget(image_label)


class AttrMenuWidget(DragMoveQListWidget2[AttrModel]):

    def __init__(self):
        super().__init__()

        self.attrs = config.data.get_depend_attrs()

        self.setSelectionMode(QListWidget.SingleSelection)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.update_all(self.attrs)

    def create_item_widget(self, data: AttrModel) -> QtWidgets.QWidget:
        return AttrItem(data)

    def data_change(self, data_array: List[AttrModel]):
        config.data.set_depend_attrs(data_array)

    def create_actions(self, item: QtWidgets.QListWidgetItem) -> Dict[int, str]:
        return {
            0: '編輯',
            1: '刪除'
        }

    def action_click(self, action_id: int, item: QtWidgets.QListWidgetItem):
        row = self.row(item)
        if action_id == 0:
            self.show_edit_dialog(item)
        elif action_id == 1:
            question(self, '確認', '確定要刪除嗎?', lambda: self.remove_item(row))

    def _on_item_double_clicked(self, item):
        self.show_edit_dialog(item)

    def show_edit_dialog(self, item):
        dialog = AttrMenuEditDialog(self.attrs, self.attrs[self.row(item)])
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.edit_item(self.row(item), dialog.get_result())

    def show_add_dialog(self):
        dialog = AttrMenuEditDialog(self.attrs)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.add_item(dialog.get_result())
