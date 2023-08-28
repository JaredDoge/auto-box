from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont


class TabListWidget(QtWidgets.QListWidget):

    def __init__(self, tabs=None):
        super().__init__()

        if tabs is None:
            tabs = []
        self.tabs = tabs

        self.setStyleSheet("""
                            TabListWidget {
                                border-top: 1px solid black;
                                border-bottom: 1px solid black;
                                border-left: 1px solid black;
                                border-right: none;
                                background-color: #F0F0F0;
                            }
                            
                            TabListWidget::item:selected {
                                background-color: white;
                                color: black; 
                            }
                           """
                           )

        self.update_all(tabs)

    def update_all(self, tabs):
        self.clear()
        self.tabs = tabs
        for tab in tabs:
            self._add_item(tab)

    def item_click_listener(self, listener):
        self.clicked.connect(listener)

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def _add_item(self, tab):
        item = QtWidgets.QListWidgetItem()
        item.setText(tab.name)
        font = QFont()
        font.setPointSize(14)
        item.setFont(font)
        self.addItem(item)

    def get_tab_name(self, index):
        if not self.tabs:
            return ''
        return self.tabs[index].name

    def add_tab(self, tab):
        self._add_item(tab)
        self.tabs.append(tab)

    def remove_tab(self, index):

        if index >= len(self.tabs) or index < 0:
            return
        self.takeItem(index)
        del self.tabs[index]
