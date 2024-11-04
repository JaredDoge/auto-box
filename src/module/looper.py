import asyncio
import threading
import time
from abc import ABC, abstractmethod

from src import config
from src.module.log import log


class TaskWrapper(ABC):

    @abstractmethod
    async def create(self, *args, **kwarg):
        pass


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

    def tasks(self, task_name):
        return [task for task in self._tasks if task.get_name() == task_name]

    def task(self, task_name):
        return next((task for task in self._tasks if task.get_name() == task_name), None)

    def is_current_task(self, task_name):
        """檢查最近的任務名稱是否為指定的名稱"""
        return self.current_task and self.current_task.get_name() == task_name

    def is_running(self, task_name):
        return any(task.get_name() == task_name for task in self._tasks)

    async def cancel_task(self, task_name=None):
        async def _cancel(task):
            if task.cancelled():
                return
            task.cancel()  # 先標記取消
            try:
                await task  # 再等待取消完成
            except asyncio.CancelledError:
                pass

        """取消指定名稱的任務或取消所有任務"""
        if task_name:
            # 取消指定名稱的任務
            tasks_to_cancel = [task for task in self._tasks if task.get_name() == task_name]

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
