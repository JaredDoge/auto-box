from PyQt5 import QtWidgets


class TargetAttrItem(QtWidgets.QWidget):
    def __init__(self, attr, parent=None):
        super().__init__(parent)

        frame_layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel(attr.attr1)
        frame_layout.addWidget(label)

        label2 = QtWidgets.QLabel(attr.attr2)
        frame_layout.addWidget(label2)

        label3 = QtWidgets.QLabel(attr.attr3)
        frame_layout.addWidget(label3)


class TargetListWidget(QtWidgets.QListWidget):

    def __init__(self, attrs=None):
        super().__init__()

        if attrs is None:
            attrs = []

        self.attrs = attrs
        self.setStyleSheet("""
                           TargetListWidget {
                               border-top: 1px solid black;
                               border-bottom: 1px solid black;
                               border-left: none;
                               border-right: 1px solid black;
                           }
                           """)
        self.update_all(attrs)

    def update_all(self, attrs):
        self.clear()
        self.attrs = attrs
        if not attrs:
            return
        for attr in attrs:
            self._add_item(attr)

    def item_click_listener(self, listener):
        self.clicked.connect(listener)

    def item_select_changed(self, listener):
        self.itemSelectionChanged.connect(listener)

    def _add_item(self, attr):
        item = QtWidgets.QListWidgetItem()
        self.addItem(item)
        widget_item = TargetAttrItem(attr)
        item.setSizeHint(widget_item.sizeHint())

        self.setItemWidget(item, widget_item)

    def add_target(self, attr):
        self._add_item(attr)
        self.attrs.append(attr)

    def remove_target(self, index):

        if index >= len(self.attrs) or index < 0:
            return
        self.takeItem(index)
        del self.attrs[index]
