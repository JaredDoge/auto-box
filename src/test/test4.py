import sys
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem, QWidget, QVBoxLayout, QLabel

# 示例自定义 widget
class RowItemWidget(QWidget):
    def __init__(self, row, data_change_callback=None):
        super().__init__()
        self.row = row
        self.data_change_callback = data_change_callback
        layout = QVBoxLayout()
        self.label = QLabel(row)
        layout.addWidget(self.label)
        self.setLayout(layout)

class CustomListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragDropMode(self.InternalMove)
        self.setSelectionMode(self.SingleSelection)

    def _add_item(self, index, row: str):
        item = QListWidgetItem()
        self.insertItem(index, item)
        widget_item = RowItemWidget(row)
        item.setSizeHint(widget_item.sizeHint())
        self.setItemWidget(item, widget_item)

    def dragMoveEvent(self, event):
        if ((target := self.row(self.itemAt(event.pos()))) ==
                (current := self.currentRow()) + 1 or
                (current == self.count() - 1 and target == -1)):
            event.ignore()
        else:
            super().dragMoveEvent(event)

    # def dropEvent(self, event):
    #     super().dropEvent(event)
    #     self._update_widgets()
    #
    # def _update_widgets(self):
    #     for i in range(self.count()):
    #         item = self.item(i)
    #         widget_item = self.itemWidget(item)
    #         self.removeItemWidget(item)
    #         self.setItemWidget(item, widget_item)
    #         item.setSizeHint(widget_item.sizeHint())

if __name__ == "__main__":
    app = QApplication(sys.argv)

    list_widget = CustomListWidget()
    rows = ["Item 0", "Item 1", "Item 2", "Item 3", "Item 4"]

    for i, row in enumerate(rows):
        list_widget._add_item(i, row)

    list_widget.setWindowTitle('Custom QListWidgetItem 拖曳排序')
    list_widget.resize(300, 200)
    list_widget.show()

    sys.exit(app.exec_())
