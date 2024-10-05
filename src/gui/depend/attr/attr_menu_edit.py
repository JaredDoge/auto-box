import copy

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyle

from src.data.depend_model import AttrModel
from src.gui.common.msg_box import information


class AttrMenuEditDialog(QtWidgets.QDialog):
    def __init__(self, attrs, model: AttrModel = None):
        super().__init__()

        self.attrs = attrs

        self.is_select = True if model else False
        self.model = copy.deepcopy(model) if model else AttrModel(name='', path='選擇對應屬性截圖路徑')
        self.origin_name = model.name if model else None  # 原始名稱

        self.setWindowTitle("增加屬性")
        self.setFixedSize(300, 150)

        layout = QtWidgets.QVBoxLayout()

        self.attr_name_input = QtWidgets.QLineEdit()
        self.attr_name_input.setPlaceholderText("輸入屬性名稱(例如:DEX+8%)")
        self.attr_name_input.setStyleSheet("font-size: 16px")
        self.attr_name_input.setText(self.model.name)
        layout.addWidget(self.attr_name_input)

        layout.addSpacing(10)

        path_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(path_layout)

        self.image_path_label = QtWidgets.QLabel()

        self.image_path_label.setWordWrap(True)
        self.image_path_label.setText(self.model.path)
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
        current_name = self.attr_name_input.text()

        if len(self.attr_name_input.text()) == 0 or not self.is_select or self.attr_name_input.text() == '空':
            information(self, "錯誤", "資料不能留白 或 '空'")
        elif (self.origin_name is None or self.origin_name != current_name) and self._find_same_name(current_name):
            information(self, "錯誤", "名稱不能重複")
        else:
            self.accept()

    def _find_same_name(self, name):
        return any(name == item.name for item in self.attrs)

    def _select_image(self):
        f = "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.ReadOnly
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "選擇圖片", filter=f, options=options)
        if file_name:
            self.is_select = True
            self.image_path_label.setText(file_name)

    def get_result(self) -> AttrModel:
        self.model.name = self.attr_name_input.text()
        self.model.path = self.image_path_label.text()
        return self.model
