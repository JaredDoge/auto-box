import asyncio
import threading
from typing import List, Tuple, Dict
from abc import ABC, abstractmethod

from src.module.log import log


# 定义抽象基类
class TaskWrapper(ABC):

    @abstractmethod
    def get_task(self) -> asyncio.Task:
        pass

    @staticmethod
    @abstractmethod
    def task_name() -> str:
        pass


class Looper:

    def __init__(self):
        # self.stop_event = asyncio.Event()
        # self.stop_event.set()
        self.loop = asyncio.new_event_loop()
        # self.tasks: Dict[str, asyncio.Task] = {}
        t = threading.Thread(target=self._start_loop, daemon=True)
        t.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, task):
        asyncio.run_coroutine_threadsafe(task, self.loop)
    def check_stop_condition(self) -> bool:
        # 自定义停止条件
        return False

    def start_all_task(self, tasks: List[TaskWrapper]):

        async def _start_tasks():
            self.stop_event.clear()
            for task in tasks:
                asyncio_task = task.get_task()
                self.tasks[task.task_name()] = asyncio_task
                # asyncio.run_coroutine_threadsafe(asyncio_task, self.loop)
            try:
                await asyncio.gather(*self.tasks.values())
                log(f"EZ")
            except asyncio.CancelledError:
                log(f"痾和")

        asyncio.run_coroutine_threadsafe(_start_tasks(), self.loop)

    def stop_all_tasks(self):
        async def _stop_all_tasks():
            for task in self.tasks.values():
                task.cancel()
            await asyncio.gather(*self.tasks.values(), return_exceptions=True)
            self.tasks.clear()
            self.stop_event.set()
            print('GGas4f65asf')

        asyncio.run_coroutine_threadsafe(_stop_all_tasks(), self.loop)

