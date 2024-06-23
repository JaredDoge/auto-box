import time

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QListWidget, QMenu, QDialogButtonBox, QMessageBox
import copy

from src import config
from src.data.macro_model import MacroRowModel, KeyboardCommandModel, DelayCommandModel, CommandModel
from src.gui.common.ignore_right_menu import IgnoreRightButtonMenu


class DelayInputDialog(QtWidgets.QDialog):
    def __init__(self, delay: DelayCommandModel = None):
        super().__init__()

        self.delay = copy.deepcopy(delay) if delay else DelayCommandModel(time=0.5)

        self.setWindowTitle("延遲時間(秒)")

        layout = QtWidgets.QVBoxLayout(self)

        # 说明标签
        explanation_label = QtWidgets.QLabel("小數點後最多2位")
        layout.addWidget(explanation_label)

        # 输入框
        self.input_edit = QtWidgets.QLineEdit()
        validator = QDoubleValidator()
        validator.setDecimals(2)
        self.input_edit.setValidator(validator)
        self.input_edit.setText(f'{self.delay.time}')
        layout.addWidget(self.input_edit)
        # self.input_edit.selectAll()

        buttons = QDialogButtonBox(QtCore.Qt.Horizontal, self)

        ok_button = QPushButton("確認")
        cancel_button = QPushButton("取消")
        buttons.addButton(ok_button, QDialogButtonBox.AcceptRole)
        buttons.addButton(cancel_button, QDialogButtonBox.RejectRole)
        ok_button.clicked.connect(self._accept)
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def _accept(self):
        if len(self.input_edit.text()) == 0:
            QtWidgets.QMessageBox.warning(self, "", "延遲時間不能空白")
            return

        if float(self.input_edit.text()) < 0:
            QtWidgets.QMessageBox.warning(self, "", "延遲時間須大於-1")
            return
        self.delay.time = float(self.input_edit.text())
        self.accept()

    def get_value(self):
        return self.delay


class CommandListWidget(QtWidgets.QListWidget):
    def __init__(self, record_signal):
        super().__init__()
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.commands = None
        self.record_signal = record_signal
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.is_recording = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and not self.is_recording:
            items = self.selectedItems()
            if len(items) > 0:
                indexes = [self.row(item) for item in items]
                head_index = min(indexes)
                tail_index = max(indexes)
                self.remove_commands(head_index, tail_index)
        else:
            super(CommandListWidget, self).keyPressEvent(event)

    def _on_item_double_clicked(self, item):
        # 錄製中不能編輯
        if self.is_recording:
            return
        self.edit_delay(self.row(item))

    def _show_context_menu(self, pos):
        # 錄製中不能編輯
        if self.is_recording:
            return

        item = self.itemAt(pos)
        if item is None:
            return
        selected_items = self.selectedItems()

        context_menu = IgnoreRightButtonMenu(self)

        edit_action = delete_action = delay_after_action = delay_before_action = \
            before_action = after_action = delete_all_action = None
        # 選到單個

        if len(selected_items) == 1:
            index = self.row(item)
            # 只有延遲時間可以編輯，按鍵會有 up 跟 down 的問題
            if isinstance(self.commands[index], DelayCommandModel):
                edit_action = context_menu.addAction("編輯")
            delay_before_action = context_menu.addAction("此前延遲")
            delay_after_action = context_menu.addAction("此後延遲")
            before_action = context_menu.addAction("此前紀錄")
            after_action = context_menu.addAction("此後紀錄")
            delete_action = context_menu.addAction("刪除")
        elif len(selected_items) > 1:
            delete_all_action = context_menu.addAction("刪除所選")

        action = context_menu.exec_(self.mapToGlobal(pos))

        if action is None:
            return
        index = self.row(item)
        if action == edit_action:
            self.edit_delay(index)
        elif action == delete_action:
            self.remove_command(index)
        elif action == before_action:
            self.record_signal.emit(index)
        elif action == after_action:
            self.record_signal.emit(index + 1)
        elif len(selected_items) > 1 and action == delete_all_action:
            indexes = [self.row(item) for item in selected_items]
            head_index = min(indexes)
            tail_index = max(indexes)
            self.remove_commands(head_index, tail_index)
        elif action == delay_after_action:
            self.add_delay(index + 1)
        elif action == delay_before_action:
            self.add_delay(index)

    def update_all(self, commands: list[CommandModel]):
        self.clear()
        self.commands = commands
        if not commands:
            return

        for index, command in enumerate(commands):
            self._add_item(index, command)

    def add_command(self, command, index=None, scroll_to_bottom=True):
        if index is None:
            index = len(self.commands)

        self._add_item(index, command)
        self.commands.insert(index, command)
        if scroll_to_bottom:
            self.scrollToBottom()

    def remove_command(self, index):
        if index >= len(self.commands) or index < 0:
            return
        self.takeItem(index)
        del self.commands[index]

    def remove_commands(self, start, end):
        for i in range(end, start - 1, -1):
            self.remove_command(i)

    def _add_item(self, index, command: CommandModel):
        def _get_format_text():
            t = ''
            if isinstance(command, DelayCommandModel):
                t = f"延遲 {command.time} 秒"
            elif isinstance(command, KeyboardCommandModel):
                t = f"{'按下' if command.event_type == 'down' else '抬起'} {command.event_name}"
            return t

        text = _get_format_text()
        item = QtWidgets.QListWidgetItem()
        item.setText(text)
        font = QFont()
        font.setPointSize(10)
        item.setFont(font)
        self.insertItem(index, item)

    def edit_command(self, index, command, focus=True):
        if index >= len(self.commands) or index < 0:
            return
        self.remove_command(index)
        self.add_command(command, index, False)
        if focus:
            self.setCurrentRow(index)

    def edit_delay(self, index):
        if index >= len(self.commands) or index < 0:
            return
        command = self.commands[index]
        if not isinstance(command, DelayCommandModel):
            return

        dialog = DelayInputDialog(command)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.edit_command(index, dialog.get_value())

    def add_delay(self, index):
        if index >= len(self.commands) or index < 0:
            return

        dialog = DelayInputDialog()
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.add_command(dialog.get_value(), index, False)


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
    block_record_signal = pyqtSignal(object)

    def __init__(self, row: MacroRowModel = None, parent=None):

        def _get_title_label(title):
            label = QtWidgets.QLabel(title)
            label_font = QFont()
            label_font.setPointSize(12)
            label.setFont(label_font)
            return label

        def _get_little_title_label(title):
            label = QtWidgets.QLabel(title)
            label_font = QFont()
            label_font.setPointSize(9)
            label.setStyleSheet("color: gray;")
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
        self.row = copy.deepcopy(row) if row else MacroRowModel(name='', run=True, interval=0.5, count=-1, commands=[])

        self.block_index = -1

        self.setWindowTitle("巨集編輯")
        self.setFixedSize(450, 575)

        layout = QVBoxLayout()
        self.setLayout(layout)

        name_title = _get_title_label("名稱:")
        layout.addWidget(name_title)

        self.name_widget = _get_edit(self.row.name)
        self.name_widget.setContentsMargins(10, 0, 0, 0)
        layout.addWidget(self.name_widget)

        command_title = _get_title_label("指令:")
        layout.addWidget(command_title)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(10, 0, 0, 0)
        self.command_list_widget = CommandListWidget(self.block_record_signal)
        h_layout.addWidget(self.command_list_widget)
        layout.addLayout(h_layout)
        self.command_list_widget.update_all(self.row.commands)

        count_title = _get_title_label("執行次數:")
        layout.addWidget(count_title)

        self.count_widget = CountSelectWidget(self.row.count)
        self.count_widget.setContentsMargins(10, 0, 0, 0)
        layout.addWidget(self.count_widget, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

        interval_title = _get_title_label("每次間隔(秒):")
        layout.addWidget(interval_title)

        interval_little_title = _get_little_title_label("小數點後最多2位")
        layout.addWidget(interval_little_title)

        self.interval_widget = _get_edit(str(self.row.interval))
        validator = QDoubleValidator()
        validator.setDecimals(2)
        self.interval_widget.setValidator(validator)
        self.interval_widget.setContentsMargins(10, 0, 0, 0)
        self.interval_widget.setFixedWidth(100)
        layout.addWidget(self.interval_widget)

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
        self.block_record_signal.connect(self.start_block_recording)

    def confirm(self):
        if len(self.name_widget.text()) <= 0:
            QtWidgets.QMessageBox.warning(self, "", "名稱不能空白")
            return

        if self.command_list_widget.count() <= 0:
            QtWidgets.QMessageBox.warning(self, "", "指令不能空白")
            return

        if not self.count_widget.is_infinity() and self.count_widget.get_count() <= 0:
            QtWidgets.QMessageBox.warning(self, "", "執行次數至少1次")
            return

        if len(self.interval_widget.text()) == 0:
            QtWidgets.QMessageBox.warning(self, "", "每次間隔不能空白")
            return

        if float(self.interval_widget.text()) < 0:
            QtWidgets.QMessageBox.warning(self, "", "每次間隔必須大於-1")
            return

        self.row.name = self.name_widget.text()
        self.row.count = self.count_widget.get_count()
        self.row.interval = abs(float(self.interval_widget.text()))  # abs避免顯示 -0 狀況
        self.accept()

    def get_result(self):
        return self.row

    def closeEvent(self, event):
        config.signal.remove_listener(self.on_event)
        super().closeEvent(event)

    def _edit_enable(self, enable):
        self.name_widget.setEnabled(enable)
        self.count_widget.setEnabled(enable)
        self.interval_widget.setEnabled(enable)
        self.confirm_button.setEnabled(enable)

    def toggle_recording(self):

        if self.recording:
            self.stop_recording()
        else:
            if len(self.row.commands) > 0:
                reply = QMessageBox.question(
                    self,
                    '確認',
                    '開始錄製會先清空目前的紀錄，確定要開始錄製嗎?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            self.row.commands.clear()
            self.command_list_widget.clear()
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.record_button.setText("停止錄製")
        self._edit_enable(False)
        self.current = None
        self.last_time = 0
        self.command_list_widget.is_recording = True
        config.signal.add_listener(self.on_event, 0)

    def stop_recording(self):
        self.block_index = -1
        self.recording = False
        self.record_button.setText("開始錄製")
        self._edit_enable(True)
        self.command_list_widget.is_recording = False
        config.signal.remove_listener(self.on_event)

    @pyqtSlot(object)
    def add_item(self, command: CommandModel):
        if self.block_index == -1:
            # 普通錄製
            self.command_list_widget.add_command(command)
        else:
            # 區塊錄製
            self.command_list_widget.add_command(command, self.block_index, False)
            self.block_index = self.block_index + 1

    @pyqtSlot(object)
    def start_block_recording(self, index: int):
        self.block_index = index
        self.start_recording()

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
        delay = round(current_time - self.last_time, 2)  # 精確到10毫秒
        self.last_time = current_time

        self.add_item_signal.emit(DelayCommandModel(time=delay))
        if event.event_type == 'down' or event.event_type == 'up':
            self.current = KeyboardCommandModel(event_name=event.name,
                                                event_type=event.event_type)
            self.add_item_signal.emit(self.current)

        # 攔截事件，不會觸發後面的監聽器
        return True
