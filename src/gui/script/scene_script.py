from PyQt5 import QtWidgets
from src import config


class SceneScript(QtWidgets.QWidget):

    def set_setting(self):
        config.data.set_setting(self.setting)

    def __init__(self):
        super().__init__()

        tab_widget = QtWidgets.QTabWidget(self)
