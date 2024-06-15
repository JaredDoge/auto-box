from PyQt5 import QtWidgets
from src import config
from src.gui.macro.main.macro_main import MacroMain


class SceneMarco(QtWidgets.QWidget):

    def set_setting(self):
        pass
        # config.data.set_setting(self.setting)

    def __init__(self):
        super().__init__()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        tab_widget = QtWidgets.QTabWidget(self)
        main_layout.addWidget(tab_widget)

        macro_main = MacroMain()
        tab_widget.addTab(macro_main, "腳本")

        tab_bar = tab_widget.tabBar()
        tab_bar.setStyleSheet("""
               QTabBar::tab 
               {
                height: 30px; 
                width: 70px;
                font-size: 18px;       
               }
               """)
