from abc import ABC, abstractmethod, ABCMeta
from typing import TypeVar, Generic, Dict, Callable, List, Optional

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QObject

from src.gui.common.ignore_right_menu import IgnoreRightButtonMenu

T = TypeVar('T')


class CombinedMeta(ABCMeta, type(QtWidgets.QWidget)):
    pass


class BaseListWidget(QtWidgets.QListWidget, Generic[T], metaclass=CombinedMeta):
    def __init__(self):
        super().__init__()

        # 通用資料陣列，用於儲存所有項目資料
        self.data_array: List[T] = []

        # 設置右鍵菜單策略
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def data(self) -> List[T]:
        return self.data_array

    def show_context_menu(self, pos: QtCore.QPoint):
        """
        顯示右鍵菜單。根據所選項目創建菜單，並調用對應的處理函數。

        參數:
            pos (QtCore.QPoint): 當前滑鼠右鍵點擊的位置。
        """
        item = self.itemAt(pos)
        if item is None:
            # 右鍵點擊的位置上需有item才觸發
            return

        # 創建上下文菜單，並傳遞當前項目
        context_menu = IgnoreRightButtonMenu(self)
        actions = self.create_actions(item)

        # 為菜單添加操作項目並設置對應的處理函數
        for action_id, action_name in actions.items():
            action = context_menu.addAction(action_name)
            action.setData(action_id)

        action = context_menu.exec_(self.mapToGlobal(pos))

        if action and action.data() is not None:
            self.action_click(action.data(), item)

    def action_click(self, action_id: int, item: QtWidgets.QListWidgetItem):
        pass

    def create_actions(self, item: QtWidgets.QListWidgetItem) -> Dict[int, str]:
        """
        返回預設的菜單操作編號及其對應的名稱。此方法必須由子類別實現，用來定義具體的菜單操作。

        參數:
            item (QtWidgets.QListWidgetItem): 目前選中的項目。

        返回:
            Dict[int, str]: 菜單操作編號與對應名稱的字典。
        """
        return {}

    @abstractmethod
    def data_change(self, data_array: List[T]):
        """
        資料變更時的處理行為。需在子類別中覆寫此方法，以實現具體的資料更新邏輯。

        參數:
            data_array (List[T]): 更新後的資料陣列。
        """
        pass

    def _add_item(self, row: int, data: T):
        """
        增加自訂的 QListWidgetItem 並設置其對應的 Widget。

        參數:
            row (int): 插入項目的行索引。
            data (T): 要顯示的資料。
        """
        item = QtWidgets.QListWidgetItem()
        self.insertItem(row, item)
        widget_item = self.create_item_widget(data)
        item.setSizeHint(widget_item.sizeHint())
        self.setItemWidget(item, widget_item)

    def add_item(self, data: T, row: Optional[int] = None, update: bool = True):
        """
        新增資料項目並插入到列表中。

        參數:
            data (T): 要新增的資料。
            row (Optional[int]): 要插入的行索引，如果為 None，則插入到最後一行。
            update (bool): 是否在新增後更新資料狀態。
        """
        if row is None:
            row = len(self.data_array)

        self._add_item(row, data)
        self.data_array.insert(row, data)
        if update:
            self.data_change(self.data_array)

    @abstractmethod
    def create_item_widget(self, data: T) -> QtWidgets.QWidget:
        """
        創建自訂的 Widget。此方法必須由子類別實現，以定義具體的 Widget 建立邏輯。

        參數:
            data (T): 要顯示的資料。

        返回:
            QtWidgets.QWidget: 建立好的自訂 Widget。
        """
        pass

    def remove_item(self, row: Optional[int] = None, update: bool = True):
        """
        移除指定行的資料項目。

        參數:
            row (Optional[int]): 要移除的行索引，若為 None，則不執行任何操作。
            update (bool): 是否在移除後更新資料狀態。
        """
        if row is None or row >= len(self.data_array) or row < 0:
            return
        self.takeItem(row)
        del self.data_array[row]
        if update:
            self.data_change(self.data_array)

    def edit_item(self, row: int, target: T, focus: bool = True):
        """
        編輯指定行的資料項目。

        參數:
            row (int): 要編輯的行索引。
            target (T): 要更新為的新資料。
            focus (bool): 是否將焦點移至編輯後的項目。
        """
        if row >= len(self.data_array) or row < 0:
            return
        self.remove_item(row, False)
        self.add_item(target, row, False)
        if focus:
            self.setCurrentRow(row)
        self.data_change(self.data_array)

    def update_all(self, data_array: List[T]) -> None:
        """
        批次更新所有資料項目。

        這個方法會清空目前的所有項目，並使用新的資料陣列 `data_array`
        來重新填充列表。此操作將刪除現有項目並創建新的項目 Widget。

        參數:
            data_array (List[T]): 新的資料陣列，用於更新列表中的項目。
        """
        self.clear()
        self.data_array = data_array

        if not data_array:
            return

        for row, item in enumerate(data_array):
            self._add_item(row, item)
