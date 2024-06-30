from abc import ABCMeta, ABC, abstractmethod

from PyQt5 import QtWidgets


class QWidgetABCMeta(type(QtWidgets.QWidget), ABCMeta):
    pass


class SwitchListener(ABC):
    @abstractmethod
    def switch(self):
        pass
