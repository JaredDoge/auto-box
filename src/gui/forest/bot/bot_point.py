import copy

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from src import config
from src.data.macro_model import MacroRowModel
from src.module import screen
from src.module.tools import mini_map


class PointEditDialog(QtWidgets.QDialog):
    point_signal = pyqtSignal(str)

    def __init__(self, model: MacroRowModel = None):
        super().__init__()

        self.model = copy.deepcopy(model) if model else MacroRowModel(name='', run=True, interval=0.5, count=-1,
                                                                      commands=[], is_point=True)

        # 設定視窗標題
        self.setWindowTitle("按F4紀錄人物定點")
        self.setFixedWidth(250)
        # 創建垂直佈局
        layout = QtWidgets.QVBoxLayout()

        # 創建 Label 並加入佈局
        self.label = QtWidgets.QLabel("", self)
        self.label.setText(f'{self.model.point}')
        layout.addWidget(self.label)

        # 創建確認按鈕
        self.button = QtWidgets.QPushButton("確認", self)
        layout.addWidget(self.button)

        # 按鈕點擊事件關閉視窗
        self.button.clicked.connect(self.accept)

        # 設定佈局
        self.setLayout(layout)

        self.point_signal.connect(self.show_point)

        config.signal.add_listener(self.on_event, 0)

        self.finished.connect(lambda result: config.signal.remove_listener(self.on_event))
    # def closeEvent(self, event):
    #     config.signal.remove_listener(self.on_event)
    #     super().closeEvent(event)

    @pyqtSlot(str)
    def show_point(self, point):
        self.label.setText(point)

    def get_result(self):
        return self.model

    def on_event(self, event):

        if event.name == 'f4':
            if event.event_type == 'down':
                full = config.window_tool.get_game_screen()
                if full is None:
                    self.model.point = (0, 0)
                    self.point_signal.emit(f'{self.model.point}')
                    return True

                mm = mini_map.find_minimap(full)
                if mm is None:
                    self.model.point = (0, 0)
                    self.point_signal.emit(f'{self.model.point}')
                    return True

                minimap = screen.cut_by_tl_br(full, mm)
                player = mini_map.find_player2(minimap)
                if player is None:
                    self.point_signal.emit('找不到人物')
                    return True
                self.model.point = player
                self.point_signal.emit(f'{self.model.point}')
            return True
