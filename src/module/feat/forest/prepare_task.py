import asyncio
from dataclasses import asdict
from typing import Callable

from src import config
from src.module.log import log
from src.module.tools import mini_map, command
from src.module.looper import TaskController
import keyboard


class PrepareTask:
    def __init__(self, controller: TaskController):
        super().__init__()
        self.controller = controller
        self.keys = asdict(config.data.get_rune_setting())

    async def create(self):
        try:
            while True:
                full_ = await config.window_tool.wait_game_screen()
                mm = mini_map.find_minimap(full_)
                if mm is None:
                    log('找不到小地圖')
                    await asyncio.sleep(0.2)
                    continue

                await asyncio.sleep(2)
                keyboard.send(self.keys['menu'])
                await asyncio.sleep(0.5)
                keyboard.send(self.keys['menu'])
                await asyncio.sleep(0.5)
                keyboard.send(self.keys['menu'])
                await asyncio.sleep(0.5)
                keyboard.send(self.keys['menu'])
                await asyncio.sleep(2)

                for i in range(4):
                    keyboard.send('down')
                    await asyncio.sleep(0.5)

                keyboard.send(self.keys['collect'])

                await asyncio.sleep(1)

                for i in range(10):
                    keyboard.send('down')
                    await asyncio.sleep(0.5)

                for i in range(5):
                    keyboard.send(self.keys['collect'])
                    await asyncio.sleep(0.5)

                return
        except asyncio.CancelledError:
            raise
