from PyQt5 import QtWidgets

from src import config
from src.gui.common.widget_abc_meta import SwitchListener, QWidgetABCMeta
from src.gui.macro.main.macro_bot import MacroBot
from src.module.feat.macro.marco_executor import MacroExecutor


def _already_stop():
    config.switch.off()


class SceneMarco(QtWidgets.QWidget, SwitchListener, metaclass=QWidgetABCMeta):

    def switch(self):
        sw = config.switch
        if sw.is_on():
            # 停止腳本
            self.executor.stop()
            sw.idle()
        elif sw.is_off():
            # 開始腳本
            self.executor.start(self.macro_bot.get_run_list())
            sw.on()

        else:
            return

    def __init__(self):
        super().__init__()
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        tab_widget = QtWidgets.QTabWidget(self)
        main_layout.addWidget(tab_widget)

        self.macro_bot = MacroBot()
        tab_widget.addTab(self.macro_bot, "腳本")

        tab_bar = tab_widget.tabBar()
        tab_bar.setStyleSheet("""
               QTabBar::tab 
               {
                height: 30px; 
                width: 70px;
                font-size: 18px;       
               }
               """)

        self.executor = MacroExecutor()
        self.executor.set_stop_callback(_already_stop)
