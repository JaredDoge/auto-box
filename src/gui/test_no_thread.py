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
    add_item_signal = pyqtSignal(object)  # 添加信号用于添加项目

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.signals = []

        # record
        self.recording = False
        self.last_time = 0
        self.current_signal: KeyboardSignalModel | None = None
        self.add_item_signal.connect(self.add_item)

        # play
        self.playing = False
        self.stop_event = threading.Event()
        self.playing_thread = None

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
        self.play_button.clicked.connect(self.toggle_playing)
        self.layout.addWidget(self.play_button)
        #
        # self.stop_button = QPushButton('Stop Recording', self)
        # self.stop_button.clicked.connect(self.stop_recording)
        # self.layout.addWidget(self.stop_button)

        # self.record_button.setShortcut('F5')

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.signals = []
        self.list_widget.clear()
        self.current_signal = None
        self.last_time = 0
        keyboard.hook(self.on_event)

    def stop_recording(self):
        self.recording = False
        keyboard.unhook_all()

    @pyqtSlot(object)
    def add_item(self, signal: SignalModel):
        self.signals.append(signal)
        text = ''
        if isinstance(signal, DelaySignalModel):
            text = f"延遲 {signal.time / 1000} 秒"
        elif isinstance(signal, KeyboardSignalModel):
            text = f"{'按下' if signal.event_type == 'down' else '抬起'} {signal.event_name}"
        self.list_widget.addItem(text)
        self.list_widget.scrollToBottom()

    def on_event(self, event):

        def _same(signal: KeyboardSignalModel):
            return signal.event_type == event.event_type and signal.event_name == event.name

        # 有快捷鍵的話這裡判斷

        if self.last_time == 0:
            if event.event_type == 'down':
                self.last_time = time.time()
                self.current_signal = KeyboardSignalModel(signal="keyboard", event_name=event.name,
                                                          event_type=event.event_type)
                self.add_item_signal.emit(self.current_signal)
            return

        if self.current_signal is not None and _same(self.current_signal):
            return

        current_time = time.time()
        delay = current_time - self.last_time
        delay_millisecond = int(delay * 1000)
        self.last_time = current_time

        self.add_item_signal.emit(DelaySignalModel(signal="delay", time=delay_millisecond))
        if event.event_type == 'down' or event.event_type == 'up':
            self.current_signal = KeyboardSignalModel(signal="keyboard", event_name=event.name,
                                                      event_type=event.event_type)
            self.add_item_signal.emit(self.current_signal)

    def toggle_playing(self):
        if self.playing:
            self.stop_playing()
        else:
            self.start_playing(interval=300)

    def start_playing(self, repetitions=-1, interval=0):
        self.playing = True
        self.stop_event.clear()
        self.playing_thread = threading.Thread(target=self.play_recording, args=(repetitions, interval))
        self.playing_thread.start()

    def stop_playing(self):
        self.playing = False
        self.stop_event.set()
        if self.playing_thread.is_alive():
            self.playing_thread.join()

    def play_recording(self, repetitions: int, interval: int):
        while repetitions != 0 and not self.stop_event.is_set():
            for signal in self.signals:
                if self.stop_event.is_set():
                    break
                if isinstance(signal, DelaySignalModel):
                    elapsed = 0
                    t = signal.time / 1000
                    while elapsed < t:
                        if self.stop_event.is_set():
                            break
                        time.sleep(0.001)
                        elapsed += 0.001
                elif isinstance(signal, KeyboardSignalModel):
                    if signal.event_type == 'down':
                        keyboard.press(signal.event_name)
                    elif signal.event_type == 'up':
                        keyboard.release(signal.event_name)
            repetitions -= 1
            elapsed = 0
            i = interval / 1000
            while elapsed < i:
                if self.stop_event.is_set():
                    break
                time.sleep(0.001)
                elapsed += 0.001


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyRecorder()
    ex.show()
    sys.exit(app.exec_())
