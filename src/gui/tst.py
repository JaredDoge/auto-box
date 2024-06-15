import sys
import threading
import time
from enum import Enum

import keyboard
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QListWidget, QPushButton, QWidget

from src.data.macro_model import SignalModel, KeyboardCommandModel, DelayCommandModel, CommandModelBase


class Signal(Enum):
    KEYBOARD = 1
    MOUSE = 2
    DELAY = 3


class KeyRecorder(QMainWindow):
    add_item_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.list_widget = None
        self.recording_thread = None
        self.init_ui()
        self.recording = False
        self.signals = []

        self.add_item_signal.connect(self.add_item)

    def init_ui(self):
        self.setWindowTitle('Key Recorder')
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        record_button = QPushButton('Start/Stop Recording (F5)', self)
        record_button.clicked.connect(self.toggle_recording)
        layout.addWidget(record_button)

        play_button = QPushButton('Play Recording', self)
        play_button.clicked.connect(self.play_recording)
        layout.addWidget(play_button)

        record_button.setShortcut('F5')

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.signals = []
        self.list_widget.clear()
        self.recording_thread = threading.Thread(target=self.record_events)
        self.recording_thread.start()

    def stop_recording(self):
        print('stop_recording')
        self.recording = False

    @pyqtSlot(object)
    def add_item(self, signal: SignalModel):
        self.signals.append(signal)
        text = ''
        if signal.command == "delay":
            text = f"延遲 {signal.time}"
        elif signal.command == "keyboard":
            text = f"{'按下' if signal.event_type == 'down' else '抬起'} {signal.event_name}"
        self.list_widget.addItem(text)
        self.list_widget.scrollToBottom()

    def record_events(self):
        last_time = 0
        current_signal = None
        while self.recording:
            event = keyboard.get_event()
            if not event:
                break

            if last_time == 0:
                if event.event_type == 'down':
                    last_time = time.time()
                    current_signal = KeyboardCommandModel(event_name=event.name, event_type=event.event_type)
                    self.add_item_signal.emit(current_signal)
                continue

            if current_signal and current_signal.event_type == event.event_type and current_signal.event_name == event.name:
                continue

            current_time = time.time()
            delay = current_time - last_time
            last_time = current_time

            self.add_item(DelayCommandModel(time=delay))
            if event.event_type == 'down' or event.event_type == 'up':
                current_signal = KeyboardCommandModel(event_name=event.name, event_type=event.event_type)
                self.add_item_signal.emit(current_signal)

            time.sleep(0.01)
    def play_recording(self):
        for signal in self.signals:
            if isinstance(signal, DelayCommandModel):
                time.sleep(signal.time)
            elif isinstance(signal, KeyboardCommandModel):
                if signal.event_type == 'down':
                    keyboard.press(signal.event_name)
                elif signal.event_type == 'up':
                    keyboard.release(signal.event_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KeyRecorder()
    ex.show()
    sys.exit(app.exec_())
