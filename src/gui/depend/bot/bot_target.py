from typing import List, Dict

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QListWidget

from src import config
from src.data.depend_model import DependTargetModel
from src.gui.common.base_list_widget import T
from src.gui.common.drag_move_qlist import DragMoveQListWidget, DragMoveQListWidget2
from src.gui.common.ignore_right_menu import IgnoreRightButtonMenu
from src.gui.common.msg_box import question
from src.gui.depend.bot.bot_target_edit import BotTargetEditDialog


class TargetAttrItem(QtWidgets.QWidget):
    def __init__(self, attr):
        super().__init__()
        frame_layout = QtWidgets.QVBoxLayout(self)
        style = '''
           QLabel  {
                font-size: 12pt;
           }
       '''
        label = QtWidgets.QLabel(attr.attr1)
        label.setStyleSheet(style)
        frame_layout.addWidget(label)

        label2 = QtWidgets.QLabel(attr.attr2)
        label2.setStyleSheet(style)
        frame_layout.addWidget(label2)

        label3 = QtWidgets.QLabel(attr.attr3)
        label3.setStyleSheet(style)
        frame_layout.addWidget(label3)

        # 添加一條分隔線
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)  # 橫向線條
        line.setStyleSheet("border: 1px solid #D0D0D0;")  # 自定義顏色
        frame_layout.addWidget(line)


class BotTargetWidget(DragMoveQListWidget2[DependTargetModel]):

    def data_change(self, data_array: List[T]):
        self.notify_change()

    def create_item_widget(self, data: T) -> QtWidgets.QWidget:
        return TargetAttrItem(data)

    def __init__(self, notify_change):
        super().__init__()

        self.attrs = config.data.get_depend_attrs()

        self.notify_change = notify_change

        self.setSelectionMode(QListWidget.SingleSelection)

        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.setStyleSheet("""
                                BotTargetWidget {
                                    border-top: 1px solid black;
                                    border-bottom: 1px solid black;
                                    border-left: none;
                                    border-right: 1px solid black;
                                }
                                """)

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

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def show_add_dialog(self):

        dialog = BotTargetEditDialog(self.attrs)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.add_item(dialog.get_result())

    def show_edit_dialog(self, item):
        dialog = BotTargetEditDialog(self.attrs, self.data_array[self.row(item)])
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            self.edit_item(self.row(item), dialog.get_result())
