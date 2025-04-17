import asyncio
import operator
import threading
from collections import deque
from typing import Callable

from src.module.feat.macro.frame_provider import FrameProvider
from src.module.looper import TaskWrapper, Looper
from src.data.macro_model import MacroRowModel
from src.data.command_model import DelayCommandModel, KeyboardCommandModel
from src.module.log import log
import keyboard


class MacroTaskWrapper(TaskWrapper):
    NAME = 'macro'

    def __init__(self, macro_rows: list[MacroRowModel], frame_provider: FrameProvider):
        self.frame_provider = frame_provider
        self.macro_rows = macro_rows
        self.all_down_keys = set()
        self._prepare_all_down_keys(macro_rows)

    def _prepare_all_down_keys(self, macro_rows: list):
        """準備所有需要按下的按鍵集合"""
        self.all_down_keys.clear()
        for macro_row in macro_rows:
            for command in macro_row.commands:
                if isinstance(command, KeyboardCommandModel) and command.event_type == 'down':
                    self.all_down_keys.add(command.event_name)

    def _release_all_key(self):
        """釋放所有按住的按鍵"""
        for key in self.all_down_keys:
            keyboard.release(key)

    async def _player(self, macro_row: MacroRowModel):
        """執行巨集指令"""
        count = macro_row.count
        key_queue = deque()
        while count != 0:
            for command in macro_row.commands:
                if isinstance(command, DelayCommandModel):
                    if command.type == 'time':
                        # 時間延遲處理
                        if not key_queue:
                            await asyncio.sleep(command.time)
                            continue
                        # key_queue 裡還有 key 代表目前還有按鈕按住
                        # 大於0.5秒判定為長按
                        remaining_time = command.time
                        if remaining_time > 0.5:
                            await asyncio.sleep(0.5)
                            remaining_time -= 0.5  # 減去 500 毫秒
                            # 每 30 毫秒重複輸出按下，直到剩餘時間小於 30 毫秒
                            while remaining_time > 0:
                                keyboard.press(key_queue[0])
                                # 如果剩餘時間大於等於 30 毫秒
                                if remaining_time >= 0.03:
                                    await asyncio.sleep(0.03)  # 等待 30 毫秒
                                    remaining_time -= 0.03
                                else:
                                    # 等待剩下的時間
                                    await asyncio.sleep(remaining_time)
                                    remaining_time = 0
                        else:
                            # 短按
                            await asyncio.sleep(remaining_time)
                    else:
                        # 邊界延遲處理
                        def _get_op(op: str):
                            """根據運算符返回對應的比較函數"""
                            if op == 'gt':
                                return operator.gt
                            elif op == 'lt':
                                return operator.lt
                            elif op == 'gte':
                                return operator.ge
                            elif op == 'lte':
                                return operator.le
                            elif op == 'eq':
                                return operator.eq

                        while True:
                            frame = self.frame_provider.get_frame()
                            minimap = frame['minimap']
                            player = minimap['player']
                            if player:
                                player_x = player[0]
                                target_x = minimap['width'] * command.ratio / 100 
                                if _get_op(command.operator)(player_x, target_x):
                                    break
                            await asyncio.sleep(0.1)
                elif isinstance(command, KeyboardCommandModel):
                    # 鍵盤指令處理
                    if command.event_type == 'down':
                        keyboard.press(command.event_name)
                        if command.event_name not in key_queue:
                            key_queue.appendleft(command.event_name)
                    elif command.event_type == 'up':
                        keyboard.release(command.event_name)
                        if command.event_name in key_queue:
                            key_queue.remove(command.event_name)

            count -= 1
            await asyncio.sleep(macro_row.interval)

    async def create(self, done: Callable):
        """創建巨集任務"""
        try:
            tasks = [self._player(macro_row) for macro_row in self.macro_rows]
            await asyncio.gather(*tasks)
            done()
        except asyncio.CancelledError:
            pass
        finally:
            self._release_all_key()
