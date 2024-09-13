from PyQt5 import QtWidgets

from src import config
from src.gui.common.widget_abc_meta import SwitchListener, QWidgetABCMeta
from src.gui.page_attr import PageAttributes
from src.gui.depend.main.depend_bot import DependBot
from src.gui.page_setting import PageSetting


class SceneDepend(QtWidgets.QWidget, SwitchListener, metaclass=QWidgetABCMeta):

    def switch(self):
        sw = config.switch
        if sw.is_on():
            # 停止腳本
            self.executor.stop()
            sw.idle()
        elif sw.is_off():
            # 開始腳本
            self.executor.start()
            sw.on()

    def __init__(self):
        super().__init__()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        tab_widget = QtWidgets.QTabWidget(self)
        main_layout.addWidget(tab_widget)

        page_bot = DependBot()
        tab_widget.addTab(page_bot, "腳本")

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


