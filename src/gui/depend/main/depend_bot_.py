from typing import List

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
import keyboard

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
        self.btn_switch = None
        self.target_list_widget = None
        self.tab_list_widget = None

        self.tab_list = config.data.get_tabs()
        self.attr_list = config.data.get_attrs()

        self.init_ui()

        self.key_signal.connect(self.switch)
        keyboard.on_release_key(DEFAULT_CONFIG['Start/Stop'], lambda _: self.key_signal.emit())

        config.switch.set_switch_listener(self.modify_switch)

    def init_ui(self):

        root_layout = QtWidgets.QVBoxLayout()
        self.setLayout(root_layout)

        # 兩個列表的水平layout
        list_layout = QtWidgets.QHBoxLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)
        root_layout.addLayout(list_layout)

        self.tab_list_widget = DependGroupWidget(self.tab_list)
        list_layout.addWidget(self.tab_list_widget, stretch=1)
        self.tab_list_widget.item_select_changed(self._tab_item_selection_changed)

        self.target_list_widget = TargetListWidget()
        list_layout.addWidget(self.target_list_widget, stretch=2)

        btn_layout = QtWidgets.QHBoxLayout()
        root_layout.addLayout(btn_layout)

        tab_btn_wid = QtWidgets.QWidget()
        btn_layout.addWidget(tab_btn_wid, stretch=1)

        tab_btn_layout = QtWidgets.QHBoxLayout(tab_btn_wid)

        tab_add = QtWidgets.QPushButton("+")
        tab_add.setFixedSize(30, 30)
        tab_add.clicked.connect(lambda: self._tab_dialog(self.tab_list_widget.add_tab))
        tab_add.setStyleSheet("font-size: 18px")
        tab_btn_layout.addWidget(tab_add)

        tab_remove = QtWidgets.QPushButton("-")
        tab_remove.setFixedSize(30, 30)
        tab_remove.setStyleSheet("font-size: 18px")
        tab_remove.clicked.connect(lambda: self._check_tab_select(self.tab_list_widget.remove_tab))
        tab_btn_layout.addWidget(tab_remove)

        target_btn_wid = QtWidgets.QWidget()
        target_btn_layout = QtWidgets.QHBoxLayout(target_btn_wid)
        btn_layout.addWidget(target_btn_wid, stretch=2)

        target_add = QtWidgets.QPushButton("+")
        target_add.setFixedSize(30, 30)
        target_add.clicked.connect(lambda: self._target_dialog(self.target_list_widget.add_target))
        target_add.setStyleSheet("font-size: 18px")
        target_btn_layout.addWidget(target_add)

        target_remove = QtWidgets.QPushButton("-")
        target_remove.setFixedSize(30, 30)
        target_remove.clicked.connect(lambda: self._check_target_select(self.target_list_widget.remove_target))
        target_remove.setStyleSheet("font-size: 18px")
        target_btn_layout.addWidget(target_remove)

        root_layout.addSpacing(20)

        self.btn_switch = QtWidgets.QPushButton(f"開始({DEFAULT_CONFIG['Start/Stop']})")
        self.btn_switch.setFixedSize(70, 50)
        self.btn_switch.clicked.connect(self.switch)
        root_layout.addWidget(self.btn_switch, alignment=Qt.AlignHCenter)

        self.tab_list_widget.setCurrentRow(0)

    def _tab_item_selection_changed(self):
        index = self.tab_list_widget.currentRow()
        if index != -1:
            self.target_list_widget.update_all(self.tab_list[index].targets)

    def _check_target_select(self, remove):
        if self.target_list_widget.currentRow() == -1:
            return
        ret = QtWidgets.QMessageBox(self).question(self, '刪除', '確定要底力特嗎?')
        if ret == QtWidgets.QMessageBox.Yes:
            remove(self.target_list_widget.currentRow())

            config.data.set_tabs(self.tab_list)

    def _check_tab_select(self, remove):
        if self.tab_list_widget.currentRow() == -1:
            return
        name = self.tab_list_widget.get_group_name(self.tab_list_widget.currentRow())
        mbox = QtWidgets.QMessageBox(self)
        ret = mbox.question(self, '刪除', f'確定要底力特 "{name}" 嗎?')
        if ret == QtWidgets.QMessageBox.Yes:
            remove(self.tab_list_widget.currentRow())
            self.target_list_widget.clear()

            config.data.set_tabs(self.tab_list)

    def _tab_dialog(self, add):
        text, ok = QtWidgets.QInputDialog().getText(self, '', '請輸入屬性群組(ex:飾品類、武器類)')
        if ok and len(text) != 0:
            add(TabModel(text))

            config.data.set_tabs(self.tab_list)

    def _target_dialog(self, add):
        if self.tab_list_widget.currentRow() == -1:
            QtWidgets.QMessageBox.warning(self, "", "先選擇左邊那排，如果那排是空的請點左邊的+")
            return

        dialog = TargetSelectDialog(self.attr_list)
        result = dialog.exec_()

        if result == QtWidgets.QDialog.Accepted:
            add(TargetAttrModel(*dialog.get_result()))

            config.data.set_tabs(self.tab_list)

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

        targets = self.tab_list[self.tab_list_widget.currentRow()].targets

        if len(targets) == 0:
            QtWidgets.QMessageBox.warning(self, "", "先新增你要的目標屬性，點右邊的+")
            return

        result = [self.convert(t) for t in targets]

        if not config.switch.is_on():
            config.bot.set_target_attrs(result)

        config.switch.toggle()
        self.modify_switch(config.switch.is_on())


