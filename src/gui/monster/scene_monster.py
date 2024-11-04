from PyQt5 import QtWidgets

from src import config
from src.gui.common.widget_abc_meta import SwitchListener, QWidgetABCMeta
from src.module.feat.monster.monster_executor import MonsterExecutor


def _already_stop():
    config.switch.off()


class SceneMonster(QtWidgets.QWidget, SwitchListener, metaclass=QWidgetABCMeta):

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

        else:
            return

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

        self.executor = MonsterExecutor()
        self.executor.set_stop_callback(_already_stop)
