from PyQt5 import QtWidgets

from src import config
from src.gui.common.widget_abc_meta import SwitchListener, QWidgetABCMeta
from src.gui.forest.bot.bot import BotWidget
from src.module.feat.forest.forest_executor import ForestExecutor


class SceneForest(QtWidgets.QWidget, SwitchListener, metaclass=QWidgetABCMeta):

    def switch(self):
        sw = config.switch
        if sw.is_on():
            # 停止腳本
            sw.idle()
            self.executor.stop()
            
        elif sw.is_off():
            # 開始腳本
            sw.on()
            self.executor.start(self.bot.get_run_list())
            

    def __init__(self):
        super().__init__()

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        tab_widget = QtWidgets.QTabWidget(self)
        main_layout.addWidget(tab_widget)

        self.bot = BotWidget()
        tab_widget.addTab(self.bot, "腳本")

        tab_bar = tab_widget.tabBar()
        tab_bar.setStyleSheet("""
            QTabBar::tab 
            {
             height: 30px; 
             width: 70px;
             font-size: 18px;       
            }
            """)

        self.executor = ForestExecutor()
        self.executor.set_stop_callback(lambda: config.switch.off())
