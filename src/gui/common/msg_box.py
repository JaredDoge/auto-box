from PyQt5.QtWidgets import QMessageBox


def question(parent, title, text, yes_callback):
    reply = QMessageBox.question(
        parent,
        title,
        text,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    if reply == QMessageBox.Yes and callable(yes_callback):
        yes_callback()


def information(parent, title, text):
    QMessageBox.information(parent,title, text)
