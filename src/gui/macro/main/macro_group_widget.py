from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont

from src import config


class MarcoGroupWidget(QtWidgets.QListWidget):

    def __init__(self, data_change):
        super().__init__()
        self.groups = None
        self.data_change = data_change

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

    def update_all(self, groups):
        self.clear()
        self.groups = groups
        for group in groups:
            self._add_item(group)

    def item_click_listener(self, listener):
        self.clicked.connect(listener)

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def _add_item(self, group):
        item = QtWidgets.QListWidgetItem()
        item.setText(group.name)
        font = QFont()
        font.setPointSize(14)
        item.setFont(font)
        self.addItem(item)

    def get_group_name(self, index):
        if not self.groups:
            return ''
        return self.groups[index].name

    def add_group(self, group):
        self._add_item(group)
        self.groups.append(group)

        self.data_change()

    def remove_group(self, index):

        if index >= len(self.groups) or index < 0:
            return
        self.takeItem(index)
        del self.groups[index]

        self.data_change()
