import asyncio

from src import config
from src.module.looper import TaskWrapper
from src.module.log import log


class WindowTask(TaskWrapper):

    def task_name(self) -> str:
        return 'window'

    def __init__(self, to_background):
        self.window = config.window
        self.to_background = to_background

    async def _run(self):
        try:
            while self.window.is_foreground():
                log('還在前景')
                await asyncio.sleep(1)
            self.to_background()
        except asyncio.CancelledError:
            log('失去焦點')

    def run_task(self) -> asyncio.Task:
        log('穿過去了')
        return asyncio.create_task(self._run())
