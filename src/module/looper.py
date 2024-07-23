import asyncio
import threading
import time
from abc import ABC, abstractmethod


class TaskWrapper(ABC):

    @abstractmethod
    async def create(self, *args, **kwarg):
        pass


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
