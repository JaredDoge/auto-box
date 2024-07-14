import asyncio

from src import config
from src.module.macro.macro_task import MacroTaskWrapper
from src.module.macro.macro_util import find_minimap, get_minimap, find_rune, find_player
from src.module.looper import TaskWrapper, Looper
from src.module.macro.resolve_rune_task import ResolveRuneTaskWrapper
from src.module.task_executor import TaskExecutor


class MonitorTaskWrapper(TaskWrapper):
    NAME = 'monitor'

    _INTERVAL = 1

    def __init__(self, executor: TaskExecutor, resolve_rune: ResolveRuneTaskWrapper, macro: MacroTaskWrapper):
        self.executor = executor
        self.current_task = ''
        self.resolve_rune = resolve_rune
        self.macro = macro

    async def _run(self, ):
        # try:
        # 找小地圖位置
        mm_tl, mm_br = await find_minimap()

        while True:

            full = await config.window_tool.get_game_screen()
            minimap = get_minimap(full, mm_tl, mm_br)

            # 找地圖輪
            rune = find_rune(minimap)
            player = find_player(minimap)
            if rune and player:
                resolve_name = ResolveRuneTaskWrapper.NAME
                if not self.executor.is_running(resolve_name):
                    self.cancel_current_task()
                    self.current_task = resolve_name

                    self.executor.execute(resolve_name, self.resolve_rune.create(rune, mm_tl, mm_br))

                await asyncio.sleep(self._INTERVAL)
                continue

            macro_name = MacroTaskWrapper.NAME
            if not self.executor.is_running(macro_name):
                self.cancel_current_task()
                self.current_task = macro_name
                self.executor.execute(macro_name, self.macro.create())

            await asyncio.sleep(self._INTERVAL)

    # except Exception as e:
    #     print(e)
    # finally:
    #     pass
    # keyboard.release('right')
    # keyboard.release('left')
    # keyboard.release('down+alt')

    def cancel_current_task(self):
        self.executor.cancel(self.current_task)

    def create(self) -> asyncio.Task:
        return asyncio.create_task(self._run())
