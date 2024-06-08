import sys
import threading
import time
from enum import Enum
from dataclasses import dataclass

import keyboard
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QListWidget, QPushButton, QWidget

# 定义 SignalModel 及其子类
@dataclass
class SignalModel:
    signal: str

@dataclass
class KeyboardSignalModel(SignalModel):
    event_name: str
    event_type: str

@dataclass
class DelaySignalModel(SignalModel):
    time: float


class Signal(Enum):
    KEYBOARD = 1
    MOUSE = 2
    DELAY = 3


class KeyRecorder(QMainWindow):
    update_signal = pyqtSignal(object)  # 使用 object 以支持传递自定义类型
    add_item_signal = pyqtSignal(object)  # 添加信号用于添加项目

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.recording = False
        self.signals = []
        self.stop_event = threading.Event()

        self.update_signal.connect(self.update_item)
        self.add_item_signal.connect(self.add_item)

    def init_ui(self):
        self.setWindowTitle('Key Recorder')
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.list_widget = QListWidget(self)
        self.layout.addWidget(self.list_widget)

        self.record_button = QPushButton('Start/Stop Recording (F5)', self)
        self.record_button.clicked.connect(self.toggle_recording)
        self.layout.addWidget(self.record_button)

        self.play_button = QPushButton('Play Recording', self)
        self.play_button.clicked.connect(self.play_recording)
        self.layout.addWidget(self.play_button)

        self.stop_button = QPushButton('Stop Recording', self)
        self.stop_button.clicked.connect(self.stop_recording)
        self.layout.addWidget(self.stop_button)

        self.record_button.setShortcut('F5')

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.stop_event.clear()
        self.signals = []
        self.list_widget.clear()
        self.recording_thread = threading.Thread(target=self.record_events)
        self.recording_thread.start()

    def stop_recording(self):
        self.recording = False
        self.stop_event.set()
        if self.recording_thread.is_alive():
            self.recording_thread.join()

    @pyqtSlot(object)
    def update_item(self, signal: SignalModel):
        text = ''
        if isinstance(signal, DelaySignalModel):
            text = f"延遲 {signal.time}"
        elif isinstance(signal, KeyboardSignalModel):
            text = f"{'按下' if signal.event_type == 'down' else '抬起'} {signal.event_name}"
        self.list_widget.addItem(text)
        self.list_widget.scrollToBottom()

    @pyqtSlot(object)
    def add_item(self, signal: SignalModel):
        self.signals.append(signal)
        self.update_signal.emit(signal)

    def record_events(self):
        last_time = 0
        current_signal: KeyboardSignalModel

        def on_event(event):
            nonlocal last_time, current_signal
            if self.stop_event.is_set():
                keyboard.unhook_all()
                return

            if last_time == 0:
                if event.event_type == 'down':
                    last_time = time.time()
                    current_signal = KeyboardSignalModel(signal="keyboard", event_name=event.name, event_type=event.event_type)
                    self.add_item_signal.emit(current_signal)
                return

            if current_signal and current_signal.event_type == event.event_type and current_signal.event_name == event.name:
                return

            current_time = time.time()
            delay = current_time - last_time
            last_time = current_time

            self.add_item_signal.emit(DelaySignalModel(signal="delay", time=delay))
            if event.event_type == 'down' or event.event_type == 'up':
                current_signal = KeyboardSignalModel(signal="keyboard", event_name=event.name, event_type=event.event_type)
                self.add_item_signal.emit(current_signal)

        keyboard.hook(on_event)
        self.stop_event.wait()  # 等待直到 stop_event 被设置

    def play_recording(self):
        for signal in self.signals:
            if isinstance(signal, DelaySignalModel):
                time.sleep(signal.time)
            elif isinstance(signal, KeyboardSignalModel):
                if signal.event_type == 'down':
                    keyboard.press(signal.event_name)
                elif signal.event_type == 'up':
                    keyboard.release(signal.event_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyRecorder()
    ex.show()
    sys.exit(app.exec_())
