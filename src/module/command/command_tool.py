import asyncio
import operator

import keyboard

from src.data.command_model import DelayCommandModel, KeyboardCommandModel, HorizontalBorderCommandModel
from src.data.macro_model import MacroRowModel


async def commands_player(macro_row: MacroRowModel, frame_provider):
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
                    frame = frame_provider.get_frame()
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

