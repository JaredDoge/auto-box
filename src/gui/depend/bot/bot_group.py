from typing import List, Dict

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont

from src.data.depend_model import DependModel
from src.gui.common.base_list_widget import T
from src.gui.common.drag_move_qlist import DragMoveQListWidget, DragMoveQListWidget2
from src.gui.common.ignore_right_menu import IgnoreRightButtonMenu
from src.gui.common.msg_box import question


class GroupItem(QtWidgets.QLabel):
    def __init__(self, item):
        super().__init__()
        self.setText(item.name)
        self.setStyleSheet('''
                            QLabel  {
                                    font-size: 12pt;
                                    padding-left: 2px;
                                    padding-top: 8px;
                                    padding-bottom: 8px;
                                }
                            ''')



class BotGroupWidget(DragMoveQListWidget2[DependModel]):

    def data_change(self, data_array: List[DependModel]):
        self.notify_change()

    def create_item_widget(self, data: T) -> QtWidgets.QWidget:
        return GroupItem(data)

    def __init__(self, notify_change):
        super().__init__()

        self.notify_change = notify_change

        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.setStyleSheet("""
                            BotGroupWidget {
                                border-top: 1px solid black;
                                border-bottom: 1px solid black;
                                border-left: 1px solid black;
                                border-right: none;
                                background-color: #F0F0F0;
                            }

                            BotGroupWidget::item:selected {
                                background-color: white;
                                color: black;
                            }
                           """
                           )

    def _on_item_double_clicked(self, item):
        self.show_edit_dialog(item)

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def action_click(self, action_id: int, item: QtWidgets.QListWidgetItem):
        row = self.row(item)
        if action_id == 0:
            self.show_edit_dialog(item)
        elif action_id == 1:
            question(self, '確認', '確定要刪除嗎?', lambda: self.remove_item(row))

    def create_actions(self, item: QtWidgets.QListWidgetItem) -> Dict[int, str]:
        return {
            0: '編輯',
            1: '刪除'
        }

    def show_add_dialog(self):
        text, ok = QtWidgets.QInputDialog().getText(self, '', '請輸入目標屬性群組名稱')
        if ok:
            if len(text) == 0:
                QtWidgets.QMessageBox.warning(self, "", "群組名稱不能空白")
                return

            self.add_item(DependModel(text))

    def show_edit_dialog(self, item):
        model = self.data_array[self.row(item)]
        text, ok = QtWidgets.QInputDialog().getText(self, '', '請輸入目標屬性群組名稱', text=model.name)
        if ok:
            if len(text) == 0:
                QtWidgets.QMessageBox.warning(self, "", "群組名稱不能空白")
                return
            model.name = text
            self.edit_item(self.row(item), model)
