import os

import cv2
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QStyle
from PyQt5.QtCore import Qt
from src.data.data import AttrModel, Data
from src import config
from src.module.cv import cv_imread


class AttrItem(QtWidgets.QWidget):
    def __init__(self, attr, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QHBoxLayout(self)

        label = QtWidgets.QLabel(attr.name)
        label.setStyleSheet("font-size: 16px")
        layout.addWidget(label)

        image_label = QtWidgets.QLabel()
        if os.path.exists(attr.path):
            pixmap = QPixmap(attr.path).scaledToHeight(25)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("圖片不在R")

        layout.addWidget(image_label)


class AttrInputDialog(QtWidgets.QDialog):
    def __init__(self, list_, parent=None):
        super().__init__(parent)

        self.is_select = False
        self.list = list_

        self.setWindowTitle("增加屬性")
        self.setFixedSize(300, 150)

        layout = QtWidgets.QVBoxLayout()

        self.attr_name_input = QtWidgets.QLineEdit()
        self.attr_name_input.setPlaceholderText("輸入屬性名稱(例如:DEX+8%)")
        self.attr_name_input.setStyleSheet("font-size: 16px")
        layout.addWidget(self.attr_name_input)

        layout.addSpacing(10)

        path_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(path_layout)

        self.image_path_label = QtWidgets.QLabel()

        self.image_path_label.setText("選擇對應屬性截圖路徑")
        self.image_path_label.setStyleSheet("font-size: 16px")
        path_layout.addWidget(self.image_path_label, stretch=1,
                              alignment=Qt.AlignLeft | Qt.AlignVCenter)
        layout.addStretch(1)

        select_image_button = QtWidgets.QPushButton()
        select_image_button.clicked.connect(self._select_image)
        select_image_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        path_layout.addWidget(select_image_button)

        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(self._check_empty)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def _check_empty(self):
        if len(self.attr_name_input.text()) == 0 or not self.is_select or self.attr_name_input.text() == '空':
            mbox = QtWidgets.QMessageBox(self)  # 加入對話視窗
            mbox.information(self, "錯誤", "資料不能留白 或 '空'")
        elif not self._name_unique(self.attr_name_input.text()):
            mbox = QtWidgets.QMessageBox(self)  # 加入對話視窗
            mbox.information(self, "錯誤", "名稱不能重複R")
        else:
            self.accept()

    def _name_unique(self, name):
        return not any(name == item.name for item in self.list)

    def _select_image(self):
        f = "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "選擇圖片", filter=f, options=options)
        if file_name:
            self.is_select = True
            self.image_path_label.setText(file_name)

    def get_input(self):
        return self.attr_name_input.text(), self.image_path_label.text()


class PageAttributes(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.attrs = config.data.get_attrs()
        self.templates = config.data.get_templates()

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.list_widget = QtWidgets.QListWidget()
        layout.addWidget(self.list_widget)

        self.btn_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(self.btn_layout)

        add_button = QtWidgets.QPushButton("+")
        add_button.setFixedSize(50, 50)
        add_button.clicked.connect(lambda: self._attr_dialog(self.add_attr))
        add_button.setStyleSheet("font-size: 30px")
        self.btn_layout.addWidget(add_button)

        remove_button = QtWidgets.QPushButton("-")
        remove_button.setFixedSize(50, 50)
        remove_button.clicked.connect(lambda: self._check_select(self.remove_item))
        remove_button.setStyleSheet("font-size: 30px")
        self.btn_layout.addWidget(remove_button)

        self.update_all(self.attrs)

    def _check_select(self, remove):
        if self.list_widget.currentRow() == -1:
            return
        mbox = QtWidgets.QMessageBox(self)
        ret = mbox.question(self, '刪除', '確定要底力特嗎?')
        if ret == QtWidgets.QMessageBox.Yes:
            remove(self.list_widget.currentRow())
            # 保存
            config.data.set_attrs(self.attrs)

    def _attr_dialog(self, add):
        dialog = AttrInputDialog(self.attrs)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            attr_name, image_path = dialog.get_input()
            add(AttrModel(attr_name, image_path))
            # 保存
            config.data.set_attrs(self.attrs)

    def update_all(self, attrs):
        self.list_widget.clear()
        self.attrs = attrs
        for attr in attrs:
            self._add_item(attr)

    def _add_item(self, attr):
        item = QtWidgets.QListWidgetItem()
        self.list_widget.addItem(item)
        widget_item = AttrItem(attr)
        item.setSizeHint(widget_item.sizeHint())
        self.list_widget.setItemWidget(item, widget_item)

    def add_attr(self, attr):
        self._add_item(attr)
        self.attrs.append(attr)
        self.templates[attr.name] = cv_imread(attr.path)

    def remove_item(self, index):

        if index >= len(self.attrs) or index < 0:
            return
        self.list_widget.takeItem(index)
        if self.attrs[index].name in self.templates:
            del self.templates[self.attrs[index].name]
        del self.attrs[index]




