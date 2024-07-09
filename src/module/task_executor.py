import asyncio
from typing import Dict

from src import config


class TaskExecutor:
    def __init__(self, looper=config.looper):
        self.looper = looper
        self.tasks: Dict[str, asyncio.Task] = {}

    def is_running(self, name: str):
        return name in self.tasks

    def execute(self, name: str, task: asyncio.Task):
        if self.is_running(name):
            return
        self.tasks[name] = task
        self.looper.run(task)

    async def _cancel_task(self, name: str):
        task = self.tasks[name]
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def cancel(self, name: str):
        if not self.is_running(name):
            return

        async def _cancel():
            await self._cancel_task(name)
            del self.tasks[name]

        self.looper.run(_cancel())

    async def cancel_async(self, name: str):
        if not self.is_running(name):
            return
        await asyncio.wrap_future(self.looper.run(self._cancel_task(name)))
        del self.tasks[name]

    def cancel_all(self):
        async def _cancel():
            for task in self.tasks.values():
                task.cancel()
            try:
                await asyncio.gather(*self.tasks.values(), return_exceptions=True)
            except asyncio.CancelledError:
                pass
            self.tasks.clear()

        self.looper.run(_cancel())

    async def cancel_all_async(self):
        async def _cancel():
            for task in self.tasks.values():
                task.cancel()
            try:
                await asyncio.gather(*self.tasks.values(), return_exceptions=True)
            except asyncio.CancelledError:
                pass
            self.tasks.clear()

        await asyncio.wrap_future(self.looper.run(_cancel()))
