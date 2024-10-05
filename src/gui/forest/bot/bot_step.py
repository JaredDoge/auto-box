from typing import List, Dict

from PyQt5 import QtWidgets

from src.data.macro_model import MacroGroupModel
from src.gui.common.base_list_widget import T, BaseListWidget


class StepItemWidget(QtWidgets.QLabel):
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


class BotStepWidget(BaseListWidget[MacroGroupModel]):

    def data_change(self, data_array: List[MacroGroupModel]):
        self.notify_change()

    def create_item_widget(self, data: MacroGroupModel) -> QtWidgets.QWidget:
        return StepItemWidget(data)

    def __init__(self, notify_change):
        super().__init__()

        self.notify_change = notify_change

        self.setStyleSheet("""
                            BotStepWidget {
                                border-top: 1px solid black;
                                border-bottom: 1px solid black;
                                border-left: 1px solid black;
                                border-right: none;
                                background-color: #F0F0F0;
                            }

                            BotStepWidget::item:selected {
                                background-color: white;
                                color: black;
                            }
                           """
                           )

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def create_actions(self, item: QtWidgets.QListWidgetItem) -> Dict[int, str]:
        return {}

