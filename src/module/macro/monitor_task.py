import asyncio

from src import config
from src.module.macro.macro_util import find_minimap, get_minimap, find_rune
from src.module.looper import TaskWrapper, Looper


class MonitorTaskWrapper(TaskWrapper):
    NAME = 'monitor'

    def __init__(self):
        pass

    async def _run(self):
        try:
            while True:
                # 遊戲截圖
                frame = config.window_tool.get_game_screen()
                # 找小地圖位置
                mm_tl, mm_br = find_minimap(frame)

                while True:
                    frame = config.window_tool.get_game_screen()
                    minimap = get_minimap(frame, mm_tl, mm_br)
                    # 找地圖輪
                    rune = find_rune(minimap)

                    if rune is None:
                        pass

        except Exception as e:
            print(e)
        finally:
            pass
            # keyboard.release('right')
            # keyboard.release('left')
            # keyboard.release('down+alt')

    def run_task(self) -> asyncio.Task:
        return asyncio.create_task(self._run())
