import asyncio
import operator
from collections import deque

import keyboard

from src.data.command_model import DelayCommandModel, KeyboardCommandModel
from src.data.macro_model import MacroRowModel


async def commands_player(macro_row: MacroRowModel):
    def _release_all_key():
        while key_queue:
            element = key_queue.popleft()
            keyboard.release(element)

    key_queue = deque()
    try:
        count = macro_row.count
        while count != 0:
            for command in macro_row.commands:
                if isinstance(command, DelayCommandModel):
                    if not key_queue:
                        # 目前無按鈕按住，直接 delay
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
                elif isinstance(command, KeyboardCommandModel):
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
    except asyncio.CancelledError:
        raise
    finally:
        _release_all_key()
