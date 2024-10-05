import asyncio
import operator
import threading
from typing import Callable

from src.module.looper import TaskWrapper, Looper
from src.data.macro_model import MacroRowModel
from src.data.command_model import HorizontalBorderCommandModel, DelayCommandModel, KeyboardCommandModel
from src.module.log import log
import keyboard

from src.module.macro.frame_provider import FrameProvider


class MacroTaskWrapper(TaskWrapper):

    NAME = 'macro'

    def __init__(self, macro_rows: list[MacroRowModel], frame_provider: FrameProvider):
        self.frame_provider = frame_provider
        self.macro_rows = macro_rows
        self.all_down_keys = set()
        self._prepare_all_down_keys(macro_rows)

    def _prepare_all_down_keys(self, macro_rows: list):
        self.all_down_keys.clear()
        for macro_row in macro_rows:
            for command in macro_row.commands:
                if isinstance(command, KeyboardCommandModel) and command.event_type == 'down':
                    self.all_down_keys.add(command.event_name)

    def _release_all_key(self):
        for key in self.all_down_keys:
            keyboard.release(key)

    async def _player(self, macro_row: MacroRowModel):
        count = macro_row.count

        while count != 0:
            for command in macro_row.commands:
                if isinstance(command, DelayCommandModel):
                    # log(f"延遲 {command.time} 秒")
                    await asyncio.sleep(command.time)
                elif isinstance(command, KeyboardCommandModel):
                    if command.event_type == 'down':
                        keyboard.press(command.event_name)
                        # log(f"按下 {command.event_name}")
                    elif command.event_type == 'up':
                        keyboard.release(command.event_name)
                        # log(f"抬起 {command.event_name}")
                elif isinstance(command, HorizontalBorderCommandModel):
                    def _get_op(op: str):
                        if op == 'gt':
                            return operator.gt
                        elif op == 'lt':
                            return operator.lt
                        elif op == 'ge':
                            return operator.ge
                        elif op == 'le':
                            return operator.le

                    while True:
                        frame = self.frame_provider.get_frame()
                        minimap = frame['minimap']
                        player = minimap['player']
                        if player:
                            player_x = player[0]
                            target_x = minimap['width'] * command.ratio
                            if _get_op(command.operator)(player_x, target_x):
                                break
                        await asyncio.sleep(0.1)

            count -= 1
            # log(f"間隔 {macro_row.interval} 秒")
            await asyncio.sleep(macro_row.interval)

    async def create(self, done: Callable):
        try:
            tasks = [self._player(macro_row) for macro_row in self.macro_rows]
            await asyncio.gather(*tasks)
            done()
        except asyncio.CancelledError:
            pass
        finally:
            self._release_all_key()
