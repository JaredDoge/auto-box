import abc
import asyncio

from src import config
from src.module.looper import TaskController, Looper
from abc import ABC, abstractmethod


class FrameProvider(ABC):
    @abstractmethod
    def frame(self):
        return NotImplemented


class Monitor(TaskController, FrameProvider):

    async def create(self, *args, **kwarg):
        while True:
            self._frame = config.window_tool.get_game_screen()
            await asyncio.sleep(self._interval)

    def __init__(self, looper: Looper = None, interval=0.2):
        super().__init__(looper)
        self._interval = interval
        self._frame = None
        self._running = False

    def start(self):
        async def _run():
            self.run_task('monitor', self.create())

        if self._running:
            return
        self._running = True
        self.launch(_run())

    async def stop(self):
        await self.cancel_task()
        self._running = False
        self._frame = None

    def frame(self):
        return self._frame
    

    def interval(self):
        return self._interval

    def running(self):
        return self._running
