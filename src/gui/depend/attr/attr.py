from PyQt5 import QtWidgets, QtCore
from src.gui.depend.attr.attr_menu import AttrMenuWidget


class AttrWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.list_widget = AttrMenuWidget()
        layout.addWidget(self.list_widget)

        add_button = QtWidgets.QPushButton("+")
        add_button.setFixedSize(30, 30)
        add_button.setStyleSheet("font-size: 18px")
        add_button.clicked.connect(lambda: self.list_widget.show_add_dialog())

        layout.addWidget(self.list_widget, stretch=1)
        layout.addSpacing(20)
        layout.addWidget(add_button, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(20)
