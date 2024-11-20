import asyncio
import threading
import time
from abc import ABC, abstractmethod
from enum import Enum

from src import config
from src.module.log import log


class TaskWrapper(ABC):

    @abstractmethod
    async def create(self, *args, **kwarg):
        pass


class MatchType(Enum):
    EXACT = "exact"  # 完全匹配
    STARTS_WITH = "starts_with"  # 開始字串匹配
    CONTAINS = "contains"  # 包含字串匹配


class TaskController:
    def __init__(self, looper=None):
        if looper is None:
            looper = config.looper
        self._looper = looper
        self._tasks = []  # 任務列表

    @property
    def current_task(self):
        """返回最近的任務，即列表中的最後一個任務"""
        return self._tasks[-1] if self._tasks else None

    def tasks(self, task_name, match_type=MatchType.EXACT):
        """
        根據給定的任務名稱和匹配類型返回任務列表。

        參數：
        - task_name: 要匹配的任務名稱或子字串
        - match_type: 指定匹配類型
        """
        if match_type == MatchType.STARTS_WITH:
            return [task for task in self._tasks if task.get_name().startswith(task_name)]
        elif match_type == MatchType.CONTAINS:
            return [task for task in self._tasks if task_name in task.get_name()]
        else:
            # 默認為 MatchType.EXACT
            return [task for task in self._tasks if task.get_name() == task_name]

    def task(self, task_name, match_type=MatchType.EXACT):
        """
        根據給定的任務名稱和匹配類型返回單個任務。

        參數：
        - task_name: 要匹配的任務名稱或子字串
        - match_type: 指定匹配類型
        """
        tasks = self.tasks(task_name, match_type)
        return tasks[0] if tasks else None

    def is_running(self, task_name, match_type=MatchType.EXACT):
        """檢查是否有任務正在運行，並支持匹配類型"""
        return any(self.tasks(task_name, match_type))

    async def cancel_task(self, task_name=None, match_type=MatchType.EXACT):
        """
        取消指定名稱的任務，並支援使用匹配類型（match_type）來篩選任務。
        """

        async def _cancel(task):
            if task.cancelled():
                return
            task.cancel()  # 先標記取消
            try:
                await task  # 再等待取消完成
            except asyncio.CancelledError:
                pass

        if task_name:
            # 根據 match_type 選擇篩選條件
            tasks_to_cancel = self.tasks(task_name, match_type)

            # 先取消所有匹配的任務
            for task in tasks_to_cancel:
                task.cancel()

            # 再等待它們的完成
            for task in tasks_to_cancel:
                await _cancel(task)
        else:
            # 取消所有任務
            for task in self._tasks:
                task.cancel()  # 先標記取消

            # 再等待它們的完成
            for task in self._tasks:
                await _cancel(task)

    def launch(self, coroutine):
        self._looper.run(coroutine)

    def run_task(self, task_name, coroutine):
        """創建新任務並將其添加到任務列表中"""
        task = self._looper.run_task(coroutine)
        task.set_name(task_name)
        self._tasks.append(task)
        task.add_done_callback(self._on_task_done)  # 任務結束時觸發回調
        return task

    def _on_task_done(self, task):
        """處理任務完成的邏輯，將任務從列表中移除"""
        if task in self._tasks:
            self._tasks.remove(task)


class Looper:

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()

    def run_task(self, coroutine):
        return self.loop.create_task(coroutine)

    def run(self, coroutine):
        asyncio.run_coroutine_threadsafe(coroutine, self.loop)
