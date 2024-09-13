from typing import List

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont

from src import config
from src.data.data import TabModel, TargetAttrModel
from src.gui.depend.main.depend_group_widget import DependGroupWidget
from src.gui.target_attr_list import TargetListWidget
from src.module.bot import Target

DEFAULT_CONFIG = {
    'Start/Stop': 'f4',
}


class TargetSelectDialog(QtWidgets.QDialog):
    def __init__(self, attrs, parent=None):
        super().__init__(parent)

        self.list = [i.name for i in attrs]
        self.list.insert(0, "空")

        self.setWindowTitle("選擇你想洗的屬性(屬性好的最好在上面)")
        self.setFixedSize(300, 150)

        layout = QtWidgets.QVBoxLayout()

        self.box1 = QtWidgets.QComboBox()  # 加入下拉選單
        self.box1.addItems(self.list)
        layout.addWidget(self.box1)

        self.box2 = QtWidgets.QComboBox()  # 加入下拉選單
        self.box2.addItems(self.list)
        layout.addWidget(self.box2)

        self.box3 = QtWidgets.QComboBox()  # 加入下拉選單
        self.box3.addItems(self.list)
        layout.addWidget(self.box3)

        ok_button = QtWidgets.QPushButton("OK")
        ok_button.clicked.connect(self._check_empty)
        layout.addWidget(ok_button)
        self.setLayout(layout)

    def _check_empty(self):
        combo_boxes = [self.layout().itemAt(i).widget() for i in range(3)]
        selected_count = sum(1 for combo_box in combo_boxes if combo_box.currentText() != "空")

        if selected_count == 0:
            QtWidgets.QMessageBox.warning(self, "警告", "至少要選擇一個選項")
        else:
            self.accept()

    def get_result(self):
        return self.box1.currentText(), self.box2.currentText(), self.box3.currentText()


class DependBot(QtWidgets.QWidget):
    key_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.group_widget = None
        self.row_widget = None

        self.group_list = config.data.get_tabs()
        self.attr_list = config.data.get_attrs()

        self.init_ui()

    def init_ui(self):
        def _title_style(widget):
            font = QFont()
            font.setPointSize(14)
            widget.setFont(font)
            widget.setStyleSheet('''
                                QWidget {
                                    padding: 8px
                                }
                                ''')

        list_layout = QtWidgets.QHBoxLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)
        self.setLayout(list_layout)

        # 左邊的群組列表
        group_layout = QtWidgets.QVBoxLayout()

        self.group_widget = DependGroupWidget(self._data_change)  # 帶入資料監聽器，有資料異動呼叫
        self.group_widget.item_select_changed(self._group_item_selection_changed)
        self.group_widget.update_all(self.group_list)
        group_add = QtWidgets.QPushButton("+")
        group_add.setFixedSize(30, 30)
        group_add.setStyleSheet("font-size: 18px")
        group_add.clicked.connect(lambda: self.group_widget.show_add_dialog())

        group_title = QtWidgets.QLabel("群組")
        _title_style(group_title)
        group_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        group_layout.addWidget(group_title)
        group_layout.addWidget(self.group_widget, stretch=1)
        group_layout.addSpacing(20)
        group_layout.addWidget(group_add, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        group_layout.addSpacing(20)

        # 右邊的指令列表
        row_layout = QtWidgets.QVBoxLayout()
        self.row_widget = TargetListWidget()  # 帶入資料監聽器，有資料異動呼叫

        row_add = QtWidgets.QPushButton("+")
        row_add.setFixedSize(30, 30)
        row_add.setStyleSheet("font-size: 18px")
        row_add.clicked.connect(lambda: self._row_dialog())

        row_title = QtWidgets.QLabel("目標屬性")
        _title_style(row_title)
        row_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        row_layout.addWidget(row_title)
        row_layout.addWidget(self.row_widget, stretch=1)
        row_layout.addSpacing(20)
        row_layout.addWidget(row_add, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        row_layout.addSpacing(20)

        # 将两个垂直布局添加到水平布局中
        list_layout.addLayout(group_layout, stretch=1)
        list_layout.addLayout(row_layout, stretch=2)

        self.group_widget.setCurrentRow(0)

    def _data_change(self):
        config.data.set_tabs(self.group_list)

    def _group_item_selection_changed(self):
        index = self.group_widget.currentRow()
        if index != -1:
            self.row_widget.update_all(self.group_list[index].targets)

    def _row_dialog(self):
        if self.group_widget.currentRow() == -1:
            QtWidgets.QMessageBox.warning(self, "", "請先選擇群組")
            return

        self.row_widget.show_add_dialog()

    # def _tab_item_selection_changed(self):
    #     index = self.tab_list_widget.currentRow()
    #     if index != -1:
    #         self.target_list_widget.update_all(self.group_list[index].targets)

    def _check_target_select(self, remove):
        if self.target_list_widget.currentRow() == -1:
            return
        ret = QtWidgets.QMessageBox(self).question(self, '刪除', '確定要底力特嗎?')
        if ret == QtWidgets.QMessageBox.Yes:
            remove(self.target_list_widget.currentRow())

            config.data.set_tabs(self.group_list)

    def _check_tab_select(self, remove):
        if self.tab_list_widget.currentRow() == -1:
            return
        name = self.tab_list_widget.get_group_name(self.tab_list_widget.currentRow())
        mbox = QtWidgets.QMessageBox(self)
        ret = mbox.question(self, '刪除', f'確定要底力特 "{name}" 嗎?')
        if ret == QtWidgets.QMessageBox.Yes:
            remove(self.tab_list_widget.currentRow())
            self.target_list_widget.clear()

            config.data.set_tabs(self.group_list)

    def _tab_dialog(self, add):
        text, ok = QtWidgets.QInputDialog().getText(self, '', '請輸入屬性群組(ex:飾品類、武器類)')
        if ok and len(text) != 0:
            add(TabModel(text))

            config.data.set_tabs(self.group_list)

    def _target_dialog(self, add):
        if self.tab_list_widget.currentRow() == -1:
            QtWidgets.QMessageBox.warning(self, "", "先選擇左邊那排，如果那排是空的請點左邊的+")
            return

        dialog = TargetSelectDialog(self.attr_list)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            add(TargetAttrModel(*dialog.get_result()))

            config.data.set_tabs(self.group_list)

    def convert(self, target_attr: TargetAttrModel) -> List[Target]:
        attr_counts = {}
        for attr_name in ["attr1", "attr2", "attr3"]:
            attr_value = getattr(target_attr, attr_name)

            if attr_value == '空':
                continue

            if attr_value in attr_counts:
                attr_counts[attr_value] += 1
            else:
                attr_counts[attr_value] = 1
        result_models = [Target(attr=attr, count=count) for attr, count in attr_counts.items()]
        return result_models

    def modify_switch(self, open_):
        key = DEFAULT_CONFIG["Start/Stop"]
        self.btn_switch.setText(
            f'停止({key})' if open_ else f'開始({key})')

    @pyqtSlot()
    def switch(self, _=None):

        if self.tab_list_widget.currentRow() == -1:
            QtWidgets.QMessageBox.warning(self, "", "先選擇左邊那排，如果那排是空的請點左邊的+")
            return

        targets = self.group_list[self.tab_list_widget.currentRow()].targets

        if len(targets) == 0:
            QtWidgets.QMessageBox.warning(self, "", "先新增你要的目標屬性，點右邊的+")
            return

        result = [self.convert(t) for t in targets]

        if not config.switch.is_on():
            config.bot.set_target_attrs(result)

        config.switch.toggle()
        self.modify_switch(config.switch.is_on())
