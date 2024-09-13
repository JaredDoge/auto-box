from PyQt5 import QtWidgets


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
