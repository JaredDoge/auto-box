from abc import ABC

from PyQt5 import QtWidgets, QtCore

from src.gui.common.base_list_widget import BaseListWidget, T


class DragMoveQListWidget(QtWidgets.QListWidget):

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QtWidgets.QListWidget.InternalMove)

    def dragMoveEvent(self, event):
        # fix bug
        # 修正移動列表時會發生空白item
        # https://stackoverflow.com/questions/74263946/widget-inside-qlistwidgetitem-disappears-after-internal-move
        if ((target := self.row(self.itemAt(event.pos()))) ==
                (current := self.currentRow()) + 1 or
                (current == self.count() - 1 and target == -1)):
            event.ignore()
        else:
            super().dragMoveEvent(event)


class DragMoveQListWidget2(BaseListWidget[T], ABC):

    def __init__(self):
        super().__init__()
        self.setDragDropMode(QtWidgets.QListWidget.InternalMove)
        # 監聽行移動事件，更新資料陣列
        self.model().rowsMoved.connect(self._update_data_array)

    def dragMoveEvent(self, event):
        # fix bug
        # 修正移動列表時會發生空白item
        # https://stackoverflow.com/questions/74263946/widget-inside-qlistwidgetitem-disappears-after-internal-move
        if ((target := self.row(self.itemAt(event.pos()))) ==
                (current := self.currentRow()) + 1 or
                (current == self.count() - 1 and target == -1)):
            event.ignore()
        else:
            super().dragMoveEvent(event)

    def _update_data_array(self, parent: QtCore.QModelIndex, start: int, end: int, destination: QtCore.QModelIndex,
                           row: int):
        """
        更新資料陣列的順序。當行移動時，自動調整資料的順序。

        參數:
            parent (QtCore.QModelIndex): 行的父級索引。
            start (int): 起始行的索引。
            end (int): 結束行的索引。
            destination (QtCore.QModelIndex): 目標行的父級索引。
            row (int): 目標行的索引。
        """
        # 將移動的資料從舊位置彈出，並插入到新位置
        pop = self.data_array.pop(start)
        if start > row:
            self.data_array.insert(row, pop)
        else:
            self.data_array.insert(row - 1, pop)
        self.data_change(self.data_array)
