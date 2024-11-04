import asyncio
from dataclasses import asdict
from typing import Callable

from src import config
from src.module import screen
from src.module.feat.buff_set import BuffSet
from src.module.feat.forest import forest_util
from src.module.log import log
from src.module.tools import mini_map, command
from src.module.looper import TaskController
from src.data.macro_model import MacroGroupModel
import keyboard

from src.module.tools.move import Move


class ForestTask:
    def __init__(self, controller: TaskController, macro_groups: list[MacroGroupModel]):
        super().__init__()
        self.controller = controller
        self.macro_groups = macro_groups
        self.move = Move(controller)
        self.keys = asdict(config.data.get_rune_setting())

    async def create(self):
        async def player_task(group):
            try:
                while True:
                    log(f'開始第{level}關腳本')
                    run = list(filter(lambda m: m.run, group.macros))
                    for t in run:
                        if t.is_point:
                            log(f'移動到{t.point}')
                            await self.move.go_point(t.point)
                            await asyncio.sleep(0.2)
                        else:
                            log(f'開始執行{t.name}')
                            await command.commands_player(t)

                    log(f'第{level}關腳本完成')
            except asyncio.CancelledError:
                raise

        async def _wander(left, right):
            try:
                while True:
                    await self.move.go_point(right)
                    await self.move.go_point(left)
            except asyncio.CancelledError:
                raise

        async def _next_level_task(current_level):
            is_pass = False
            try:
                def _get_offset_points(point):
                    x, y = point
                    # 因為副本地圖下關傳點都在地圖右邊，所以找一個傳點左邊偏移大一點的範圍
                    left_offset = (x - 3, y)  # 左邊偏移
                    right_offset = (x + 3, y)  # 右邊偏移
                    return [left_offset, right_offset]

                end_point = forest_util.get_point(current_level)[1]
                left, right = _get_offset_points(end_point)

                await self.move.go_point(left)

                # 讓人物由左邊偏移走到傳點，同時瘋狂按上過傳點
                while True:
                    full_ = await config.window_tool.wait_game_screen()
                    mm = mini_map.find_minimap(full_)
                    if mm is None:
                        # 如果找不到小地圖很有可能是過傳點中間的黑畫面
                        # 所以先停止移動腳本
                        log("找不到小地圖，過圖中")
                        await self.controller.cancel_task('next')
                        is_pass = True
                        await asyncio.sleep(0.2)
                        continue
                    mini = screen.cut_by_tl_br(full_, mm)
                    find_level = forest_util.get_level(mini)
                    if find_level is not None and find_level != current_level:
                        # 進到下關了
                        await self.controller.cancel_task('next')
                        return find_level
                    # 有些時候會有小地圖已經辨識到了，但人物跟傳點辨識不到
                    # 因為有透明度問題，所以加入is_pass變數判斷
                    # 避免下方腳本再跑一次
                    if not self.controller.is_running('next') and not is_pass:
                        log("開始跑進關左右移動腳本")
                        self.controller.run_task('next', _wander(left, right))

                    keyboard.send('up')
                    await asyncio.sleep(0.2)

            except asyncio.CancelledError:
                raise

        async def _check_level():
            while True:
                full_ = await config.window_tool.wait_game_screen()
                mm = mini_map.find_minimap(full_)
                if mm is None:
                    log('找不到小地圖')
                    await asyncio.sleep(0.2)
                    continue
                return forest_util.get_level(screen.cut_by_tl_br(full_, mm))

        async def _first_check():
            while True:
                level = await _check_level()
                if level is None:
                    log('確認關卡中')
                    await asyncio.sleep(0.2)
                    continue
                return level

        try:
            level = await _first_check()

            while True:
                log(f'目前關卡{level}')
                await BuffSet.get().check()
                while True:
                    full = await config.window_tool.wait_game_screen()

                    # geo = {'left': 23, 'top': 485, 'width': 138, 'height': 166}
                    # cut = screen.cut_by_geometry(full, geo)
                    # if forest_util.check_failure(cut):
                    #     # 關卡失敗
                    #     log("關卡失敗，重來")
                    #     await self.controller.cancel_task('player')
                    #     keyboard.send(self.keys['menu'])
                    #     await asyncio.sleep(0.5)
                    #     keyboard.send(self.keys['menu'])
                    #     await asyncio.sleep(0.5)
                    #     keyboard.send(self.keys['menu'])
                    #     await asyncio.sleep(0.5)
                    #     keyboard.send(self.keys['menu'])
                    #     await asyncio.sleep(2)
                    #     keyboard.send(self.keys['collect'])
                    #     await asyncio.sleep(2)
                    #     return

                    if level == 7:
                        # 裁切通關出現的位置
                        geo = {'left': 559, 'top': 322, 'width': 154, 'height': 85}
                        cut = screen.cut_by_geometry(full, geo)
                        if forest_util.check_pass(cut):
                            # 已經過關
                            log(f'通過關卡{level}')
                            await self.controller.cancel_task('player')
                            keyboard.send('enter')
                            await asyncio.sleep(5)
                            keyboard.send(self.keys['menu'])
                            await asyncio.sleep(0.5)
                            keyboard.send(self.keys['menu'])
                            await asyncio.sleep(0.5)
                            keyboard.send(self.keys['menu'])
                            await asyncio.sleep(0.5)
                            keyboard.send(self.keys['menu'])
                            await asyncio.sleep(0.5)
                            keyboard.send(self.keys['collect'])
                            return
                    else:
                        # 裁切clear出現的位置
                        geo = {'left': 529, 'top': 278, 'width': 325, 'height': 103}
                        cut = screen.cut_by_geometry(full, geo)
                        if forest_util.check_clear(cut):
                            log(f'通過關卡{level}')
                            await self.controller.cancel_task('player')
                            level = await _next_level_task(level)
                            break

                    if not self.controller.is_running('player'):
                        self.controller.run_task('player', player_task(self.macro_groups[level - 1]))
                    await asyncio.sleep(0.2)

        except asyncio.CancelledError:
            raise
