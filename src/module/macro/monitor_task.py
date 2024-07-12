import asyncio

from src import config
from src.module.macro.macro_util import find_minimap, get_minimap, find_rune
from src.module.looper import TaskWrapper, Looper
from src.module.macro.resolve_rune_task import ResolveRuneTaskWrapper
from src.module.task_executor import TaskExecutor


class MonitorTaskWrapper(TaskWrapper):
    NAME = 'monitor'

    def __init__(self, executor: TaskExecutor, rune: ResolveRuneTaskWrapper):
        self.executor = executor
        self.rune = rune

    async def _run(self):
        try:
            # 找小地圖位置
            mm_tl, mm_br = await find_minimap()

            while True:

                frame = config.window_tool.get_game_screen()

                minimap = get_minimap(frame, mm_tl, mm_br)

                # 找地圖輪
                rune = find_rune(minimap)
                if rune:
                    self.rune.create()


        except Exception as e:
            print(e)
        finally:
            pass
            # keyboard.release('right')
            # keyboard.release('left')
            # keyboard.release('down+alt')

    def create(self) -> asyncio.Task:
        return asyncio.create_task(self._run())
