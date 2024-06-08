from PyQt5 import QtWidgets

from src.gui.page_attr import PageAttributes
from src.gui.page_bot import PageBot
from src.gui.page_setting import PageSetting


class SceneAttachBox(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        tab_widget = QtWidgets.QTabWidget(self)

        page_bot = PageBot()
        tab_widget.addTab(page_bot, "附加")

        page_attr = PageAttributes()
        tab_widget.addTab(page_attr, "屬性")
        
        page_setting = PageSetting()
        tab_widget.addTab(page_setting, "設定")

        tab_bar = tab_widget.tabBar()
        tab_bar.setStyleSheet("""
            QTabBar::tab 
            {
             height: 30px; 
             width: 70px;
             font-size: 18px;       
            }
            """)

