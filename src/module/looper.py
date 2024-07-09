import asyncio
import threading
from abc import ABC, abstractmethod


class TaskWrapper(ABC):

    @abstractmethod
    def run_task(self, *args, **kwarg) -> asyncio.Task:
        pass


class Looper:

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        t = threading.Thread(target=self._start_loop, daemon=True)
        t.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, task):
        asyncio.run_coroutine_threadsafe(task, self.loop)
