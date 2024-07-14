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

    def execute(self, name: str, task):
        if self.is_running(name):
            return
        self.looper.run(task)
        task.add_done_callback(self._remove_task(name))
        self.tasks[name] = task


    def _remove_task(self, name: str):
        def callback(_):
            print(f"Task {name} done, removing from tasks.")
            self.tasks.pop(name, None)

        return callback

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
