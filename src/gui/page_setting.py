from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from src.data.data import Data
from src import config


class PageSetting(QtWidgets.QWidget):

    @staticmethod
    def _get_font(size):
        font = QFont()
        font.setPointSize(size)
        return font

    def _red(self, text):
        return f"<span style='color:red;'>{text}</span>"

    def _gray(self, text):
        return f"<span style='color:gray;'>{text}</span>"

    def set_setting(self):
        config.data.set_depend_rescue_setting(self.setting)

    def __init__(self):
        super().__init__()

        self.setting = config.data.get_depend_rescue_setting()

        layout = QtWidgets.QVBoxLayout()

        self.setLayout(layout)

        self.check_rescue = QtWidgets.QCheckBox('附加框不見自動搶救')
        self.check_rescue.setChecked(self.setting.rescue)
        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.check_rescue.setFont(self._get_font(14))
        self.check_rescue.clicked.connect(self.toggle_rescue)
        layout.addWidget(self.check_rescue)

        label_rescue = QtWidgets.QLabel(f"""
                                            <html>
                                              <p>1.請把{self._red('附加方塊')}跟{self._red('要洗的裝備')}放在背包{self._red('最右下那格')}</p>
                                              <p>2.背包{self._red('必須展開並每欄都要擴滿')}</p>
                                              <p>3.不要有任何東西擋到{self._red('擴充背包')}按鈕</p>
                                              <p>4.請不要開啟{self._red('除了背包以外的任何視窗')}(ex:裝備欄)</p>
                                            </html>
                                        """)
        label_rescue.setFont(self._get_font(11))
        label_rescue.setContentsMargins(14, 5, 0, 0)

        layout.addWidget(label_rescue)

        layout.addStretch(0)

    def toggle_rescue(self):
        self.setting.rescue = self.check_rescue.isChecked()
        self.set_setting()


