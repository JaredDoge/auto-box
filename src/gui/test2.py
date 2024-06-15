from PyQt5 import QtWidgets, QtCore
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QListWidget Minimum Width Example")
        self.setGeometry(100, 100, 400, 200)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QHBoxLayout(central_widget)

        # Create a QListWidget
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.list_widget.setStyleSheet("border: none;")  # Remove the border for a clean look
        self.list_widget.setMinimumWidth(20)
        # Add items to QListWidget
        for i in range(10):
            item = QtWidgets.QListWidgetItem(f"Item {i+1}")
            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)

        # Add a QSpacerItem with minimal width
        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout.addStretch(1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
