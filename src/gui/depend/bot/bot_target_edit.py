import copy

from PyQt5 import QtWidgets

from src.data.depend_model import DependTargetModel


class BotTargetEditDialog(QtWidgets.QDialog):
    _default = '空'

    def __init__(self, attrs, model: DependTargetModel = None):
        super().__init__()

        self.model = copy.deepcopy(model) if model else DependTargetModel(attr1=self._default,
                                                                          attr2=self._default,
                                                                          attr3=self._default)

        self.list = [i.name for i in attrs]
        self.list.insert(0, self._default)

        self.setWindowTitle("選擇你想洗的屬性(屬性好的最好在上面)")
        self.setFixedSize(300, 150)

        layout = QtWidgets.QVBoxLayout()

        self.box1 = QtWidgets.QComboBox()  # 加入下拉選單
        self.box1.addItems(self.list)
        self.box1.setCurrentText(self.model.attr1)
        layout.addWidget(self.box1)

        self.box2 = QtWidgets.QComboBox()  # 加入下拉選單
        self.box2.addItems(self.list)
        self.box2.setCurrentText(self.model.attr2)
        layout.addWidget(self.box2)

        self.box3 = QtWidgets.QComboBox()  # 加入下拉選單
        self.box3.addItems(self.list)
        self.box3.setCurrentText(self.model.attr3)
        layout.addWidget(self.box3)

        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(self._check_empty)
        layout.addWidget(ok_button)
        self.setLayout(layout)

    def _check_empty(self):
        combo_boxes = [self.layout().itemAt(i).widget() for i in range(3)]
        selected_count = sum(1 for combo_box in combo_boxes if combo_box.currentText() != self._default)

        if selected_count == 0:
            QtWidgets.QMessageBox.warning(self, "警告", "至少要選擇一個選項")
        else:
            self.accept()

    def get_result(self):
        self.model.attr1 = self.box1.currentText()
        self.model.attr2 = self.box2.currentText()
        self.model.attr3 = self.box3.currentText()
        return self.model
