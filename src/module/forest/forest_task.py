import asyncio
import operator
import threading
from typing import Callable

from src import config
from src.module.command import command_tool
from src.module.looper import TaskWrapper, Looper
from src.data.macro_model import MacroRowModel, MacroGroupModel
from src.data.command_model import HorizontalBorderCommandModel, DelayCommandModel, KeyboardCommandModel
from src.module.log import log
import keyboard

from src.module.macro.frame_provider import FrameProvider


class ForestTaskWrapper(TaskWrapper):
    NAME = 'forest'

    def __init__(self, macro_groups: list[MacroGroupModel], frame_provider: FrameProvider):
        self.frame_provider = frame_provider
        self.macro_groups = macro_groups
        self.all_down_keys = set()
        self._prepare_all_down_keys(macro_groups)

    def _prepare_all_down_keys(self, macro_groups: list):
        self.all_down_keys.clear()
        self.all_down_keys.update(
            command.event_name
            for group in macro_groups
            for macros in group.macros
            for command in macros.commands
            if isinstance(command, KeyboardCommandModel) and command.event_type == 'down'
        )

    def _release_all_key(self):
        for key in self.all_down_keys:
            keyboard.release(key)

    async def create(self, done: Callable):

        def _get_macros():
            return self.macro_groups[level].macros

        async def _task():
            tasks = [command_tool.commands_player(m, self.frame_provider) for m in _get_macros()]
            await asyncio.gather(*tasks)

        try:
            looper = config.looper
            level = 1

            while True:
                full = await config.window_tool.get_game_screen()

                looper.run_task(_task())  # 開始跑腳本


        except asyncio.CancelledError:
            pass
        finally:
            self._release_all_key()
