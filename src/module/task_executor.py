import asyncio
from typing import Dict
import weakref
from src import config


class TaskExecutor:
    def __init__(self, looper=config.looper):
        self.looper = looper
        self.tasks: Dict[str, asyncio.Task] = {}

    def is_running(self, name: str):
        return name in self.tasks

    def execute(self, name: str, coroutine):
        task = self.looper.run_task(coroutine)
        task.add_done_callback(self._remove_task(name))
        self.tasks[name] = task
        return task

    def _remove_task(self, name: str):
        def callback(_):
            print(f"Task {name} done, removing from tasks.")
            self.tasks.pop(name, None)

        return callback

    async def _cancel_task(self, name: str):
        if not self.is_running(name):
            return
        task = self.tasks[name]
        task.cancel()
        try:
            await task
            del self.tasks[name]
        except asyncio.CancelledError:
            pass

    def cancel(self, name: str):
        if not self.is_running(name):
            return
        self.looper.run(self._cancel_task(name))

    async def cancel_async(self, name: str):
        if not self.is_running(name):
            return
        await self.looper.run(self._cancel_task(name))

    def cancel_all(self):
        async def _cancel():
            for task in self.tasks.values():
                task.cancel()
            try:
                await asyncio.gather(*self.tasks.values())
            except asyncio.CancelledError:
                pass
            self.tasks.clear()

        self.looper.run(_cancel())

    async def cancel_all_async(self):
        async def _cancel():
            for task in self.tasks.values():
                task.cancel()
            try:
                await asyncio.gather(*self.tasks.values())
            except asyncio.CancelledError:
                pass
            self.tasks.clear()

        await self.looper.run(_cancel())
