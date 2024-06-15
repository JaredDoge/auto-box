import time

import keyboard
from PyQt5 import QtWidgets, QtCore, Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout
import copy

from src.data.macro_model import MacroRowModel, KeyboardCommandModel, DelayCommandModel, CommandModel


class CommandListWidget(QtWidgets.QListWidget):
    def __init__(self):
        super().__init__()
        self.commands = None

    def update_all(self, commands: list[CommandModel]):
        self.clear()
        self.commands = commands
        for command in commands:
            self._add_item(command)

    def add_command(self, command):
        self._add_item(command)
        self.commands.append(command)

    def remove_command(self, index):

        if index >= len(self.commands) or index < 0:
            return
        self.takeItem(index)
        del self.commands[index]

    def _add_item(self, command: CommandModel):
        def _get_format_text():
            t = ''
            if isinstance(command, DelayCommandModel):
                t = f"延遲 {command.time / 1000} 秒"
            elif isinstance(command, KeyboardCommandModel):
                t = f"{'按下' if command.event_type == 'down' else '抬起'} {command.event_name}"
            return t

        text = _get_format_text()
        item = QtWidgets.QListWidgetItem()
        item.setText(text)
        font = QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.addItem(item)

        self.scrollToBottom()


class CountSelectWidget(QtWidgets.QWidget):
    def __init__(self, count=-1):
        super().__init__()

        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        # 下拉菜单
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.addItems(["無限循環", "按次數"])
        self.combo_box.currentIndexChanged.connect(self.toggle_edit)

        self.combo_box.setFixedWidth(100)

        # 标签
        self.all_label = QtWidgets.QLabel("共")

        # 编辑框
        self.count_edit = QtWidgets.QLineEdit()
        self.count_edit.setFixedWidth(50)
        self.count_edit.setValidator(QIntValidator())

        self.unit_label = QtWidgets.QLabel("次")

        # 根据 loop_count 初始化显示样式
        if count == -1:
            self.combo_box.setCurrentIndex(0)  # 无限循环
        else:
            self.combo_box.setCurrentIndex(1)  # 按次数
            self.count_edit.setText(str(count))

        if count == -1:
            self.count_edit.hide()
            self.all_label.hide()
            self.unit_label.hide()
        # 添加到布局
        layout.addWidget(self.combo_box)
        layout.addWidget(self.all_label)
        layout.addWidget(self.count_edit)
        layout.addWidget(self.unit_label)

    def is_infinity(self):
        return self.combo_box.currentIndex() == 0

    def get_count(self):
        index = self.combo_box.currentIndex()
        if index == 0:  # 无限循环
            return -1
        elif index == 1:  # 按次数
            text = self.count_edit.text()
            try:
                count = int(text)
                return count
            except ValueError:
                return -1  # 输入不是整数，返回0

    def toggle_edit(self, index):
        if index == 0:  # 無限循環
            self.count_edit.hide()
            self.all_label.hide()
            self.unit_label.hide()
        elif index == 1:  # 按次数
            self.count_edit.show()
            self.all_label.show()
            self.unit_label.show()


class MacroRowEditDialog(QtWidgets.QDialog):
    add_item_signal = pyqtSignal(object)

    def __init__(self, row: MacroRowModel, parent=None):

        def _get_title_label(title):
            label = QtWidgets.QLabel(title)
            label_font = QFont()
            label_font.setPointSize(12)
            label.setFont(label_font)
            return label

        def _get_edit(default):
            edit = QtWidgets.QLineEdit()
            edit.setText(default)
            edit_font = QFont()
            edit_font.setPointSize(12)
            edit.setFont(edit_font)
            return edit

        super().__init__(parent)

        # 由於修改完可能不儲存，所以要用deep copy
        self.row = copy.deepcopy(row)

        self.setWindowTitle("巨集編輯")
        self.setFixedSize(450, 575)

        layout = QVBoxLayout()
        self.setLayout(layout)

        name_title = _get_title_label("名稱:")
        layout.addWidget(name_title)

        self.name = _get_edit(self.row.name)
        self.name.setContentsMargins(10, 0, 0, 0)
        layout.addWidget(self.name)

        command_title = _get_title_label("指令:")
        layout.addWidget(command_title)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(10, 0, 0, 0)
        self.command_list_widget = CommandListWidget()
        h_layout.addWidget(self.command_list_widget)
        layout.addLayout(h_layout)
        self.command_list_widget.update_all(self.row.commands)

        count_title = _get_title_label("執行次數:")
        layout.addWidget(count_title)

        self.count_widget = CountSelectWidget(self.row.count)
        self.count_widget.setContentsMargins(10, 0, 0, 0)
        layout.addWidget(self.count_widget, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        interval_title = _get_title_label("每次間隔(毫秒):")
        layout.addWidget(interval_title)

        self.interval = _get_edit(str(self.row.interval))
        self.interval.setValidator(QIntValidator())
        self.interval.setContentsMargins(10, 0, 0, 0)
        self.interval.setFixedWidth(100)
        layout.addWidget(self.interval)

        layout.addSpacing(5)

        self.record_button = QPushButton('開始錄製', self)
        self.record_button.setAutoDefault(False)  # 取消取到焦點時，按enter會觸發按鈕事件
        self.record_button.setFixedHeight(40)
        self.record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_button)

        layout.addSpacing(5)

        self.confirm_button = QPushButton("確認")
        self.confirm_button.setFixedHeight(30)
        self.confirm_button.setAutoDefault(False)  # 取消取到焦點時，按enter會觸發按鈕事件
        self.confirm_button.clicked.connect(self.confirm)

        layout.addWidget(self.confirm_button)

        # record
        self.recording = False
        self.last_time = 0

        self.current: KeyboardCommandModel | None = None

        self.add_item_signal.connect(self.add_item)

    def confirm(self):
        if len(self.name.text()) <= 0:
            QtWidgets.QMessageBox.warning(self, "", "名稱不能空白")
            return

        if self.command_list_widget.count() <= 0:
            QtWidgets.QMessageBox.warning(self, "", "指令不能空白")
            return

        if not self.count_widget.is_infinity() and self.count_widget.get_count() <= 0:
            QtWidgets.QMessageBox.warning(self, "", "執行次數至少1次")
            return

        if not self.interval.text().isnumeric() or int(self.interval.text()) < 0:
            QtWidgets.QMessageBox.warning(self, "", "每次間隔必須大於-1")
            return

        self.row.name = self.name.text()
        self.row.count = self.count_widget.get_count()
        self.row.interval = int(self.interval.text())
        self.accept()

    def get_result(self):
        return self.row

    def closeEvent(self, event):
        keyboard.unhook_all()
        super().closeEvent(event)

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
            self.record_button.setText("開始錄製")
            self.confirm_button.setEnabled(True)
        else:
            self.start_recording()
            self.record_button.setText("停止錄製")
            self.confirm_button.setEnabled(False)

    def start_recording(self):
        self.recording = True
        self.row.commands.clear()
        self.command_list_widget.clear()
        self.current = None
        self.last_time = 0
        keyboard.hook(self.on_event)

    def stop_recording(self):
        self.recording = False
        keyboard.unhook_all()

    @pyqtSlot(object)
    def add_item(self, command: CommandModel):
        self.command_list_widget.add_command(command)

    def on_event(self, event):

        def _same(command: KeyboardCommandModel):
            return command.event_type == event.event_type and command.event_name == event.name

        # 有快捷鍵的話這裡判斷

        if self.last_time == 0:
            if event.event_type == 'down':
                self.last_time = time.time()
                self.current = KeyboardCommandModel(event_name=event.name,
                                                    event_type=event.event_type)
                self.add_item_signal.emit(self.current)
            return

        if self.current is not None and _same(self.current):
            return

        current_time = time.time()
        delay = current_time - self.last_time
        delay_millisecond = int(delay * 1000)
        self.last_time = current_time

        self.add_item_signal.emit(DelayCommandModel(time=delay_millisecond))
        if event.event_type == 'down' or event.event_type == 'up':
            self.current = KeyboardCommandModel(event_name=event.name,
                                                event_type=event.event_type)
            self.add_item_signal.emit(self.current)
