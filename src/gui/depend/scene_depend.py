from PyQt5 import QtWidgets

from src import config
from src.gui.common.widget_abc_meta import SwitchListener, QWidgetABCMeta
from src.gui.depend.attr.attr import AttrWidget
from src.gui.depend.bot.bot import BotWidget
from src.module.feat.depend.depend_executor import DependExecutor


class SceneDepend(QtWidgets.QWidget, SwitchListener, metaclass=QWidgetABCMeta):

    def switch(self):
        sw = config.switch
        if sw.is_on():
            # 停止腳本
            sw.idle()
            self.executor.stop()
            
        elif sw.is_off():
            # 開始腳本
            self.executor.start(self.bot.get_run_list())
            sw.on()

    def __init__(self):
        super().__init__()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        tab_widget = QtWidgets.QTabWidget(self)
        main_layout.addWidget(tab_widget)

        self.bot = BotWidget()
        tab_widget.addTab(self.bot, "腳本")

        self.attr = AttrWidget()
        tab_widget.addTab(self.attr, "屬性")

        # page_setting = PageSetting()
        # tab_widget.addTab(page_setting, "設定")

        tab_bar = tab_widget.tabBar()
        tab_bar.setStyleSheet("""
            QTabBar::tab 
            {
             height: 30px; 
             width: 70px;
             font-size: 18px;       
            }
            """)

        self.executor = DependExecutor()
        self.executor.set_stop_callback(lambda: config.switch.off())
