import asyncio
from dataclasses import asdict
from typing import Callable

from src import config
from src.module import screen
from src.module.feat.buff_set import BuffSet
from src.module.feat.forest import forest_util
from src.module.log import log
from src.module.tools import mini_map, command
from src.module.looper import TaskController, MatchType
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
                log(f'目前關卡{level}')
                while True:
                    await BuffSet.get().check()
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

        async def _next_level_task():
            async def _wander():
                try:
                    while True:
                        await self.move.go_point(right)
                        await self.move.go_point(left)
                except asyncio.CancelledError:
                    raise

            nonlocal level  # 如果變數定義在嵌套函數的外部但在全局範圍內不可用（即局部變數），可以使用 nonlocal 關鍵字。
            is_pass = False

            log(f'通過關卡{level}')
            try:
                def _get_offset_points(point):
                    x, y = point
                    # 因為副本地圖下關傳點都在地圖右邊，所以找一個傳點左邊偏移大一點的範圍
                    left_offset = (x - 3, y)  # 左邊偏移
                    right_offset = (x + 3, y)  # 右邊偏移
                    return [left_offset, right_offset]

                end_point = forest_util.get_point(level)[1]
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
                        await self.controller.cancel_task('level/1_6/next')
                        is_pass = True
                        await asyncio.sleep(0.2)
                        continue
                    mini = screen.cut_by_tl_br(full_, mm)
                    find_level = forest_util.get_level(mini)
                    if find_level is not None and find_level != level:
                        # 進到下關了
                        await self.controller.cancel_task('level/1_6/next')
                        level = find_level
                        return
                    # 有些時候會有小地圖已經辨識到了，但人物跟傳點辨識不到
                    # 因為有透明度問題，所以加入is_pass變數判斷
                    # 避免下方腳本再跑一次
                    if not self.controller.is_running('level/1_6/next') and not is_pass:
                        log("開始跑進關左右移動腳本")
                        self.controller.run_task('level/1_6/next', _wander())

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
                level_ = await _check_level()
                if level_ is None:
                    log('確認關卡中')
                    await asyncio.sleep(0.2)
                    continue
                return level_

        async def _finish_forest():
            log(f'通過關卡{level}')
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

        async def _timeout():
            log("關卡超時，重來")
            keyboard.send(self.keys['menu'])
            await asyncio.sleep(0.5)
            keyboard.send(self.keys['menu'])
            await asyncio.sleep(0.5)
            keyboard.send(self.keys['menu'])
            await asyncio.sleep(0.5)
            keyboard.send(self.keys['menu'])
            await asyncio.sleep(2)
            keyboard.send(self.keys['collect'])
            await asyncio.sleep(2)

        try:
            level = await _first_check()
            while True:
                full = await config.window_tool.wait_game_screen()

                # 檢查超時
                if self.controller.is_running('timeout', MatchType.STARTS_WITH):
                    await asyncio.sleep(0.2)
                    continue
                geo = {'left': 23, 'top': 485, 'width': 138, 'height': 166}
                cut = screen.cut_by_geometry(full, geo)
                if forest_util.check_failure(cut):
                    # 關卡失敗
                    await self.controller.cancel_task('player', MatchType.STARTS_WITH)
                    await self.controller.cancel_task('level', MatchType.STARTS_WITH)
                    await self.controller.run_task('timeout', _timeout())
                    await asyncio.sleep(0.2)
                    return

                # 檢查過關
                if self.controller.is_running('level', MatchType.STARTS_WITH):
                    log('執行中')
                    await asyncio.sleep(0.2)
                    continue
                if level == 7:
                    # 裁切通關出現的位置
                    geo = {'left': 559, 'top': 322, 'width': 154, 'height': 85}
                    cut = screen.cut_by_geometry(full, geo)
                    if forest_util.check_pass(cut):
                        # 已經過關
                        await self.controller.cancel_task('player', MatchType.STARTS_WITH)
                        await self.controller.run_task('level/7', _finish_forest())
                        await asyncio.sleep(0.2)
                        return
                else:
                    # 裁切clear出現的位置
                    geo = {'left': 529, 'top': 278, 'width': 325, 'height': 103}
                    cut = screen.cut_by_geometry(full, geo)
                    if forest_util.check_clear(cut):
                        await self.controller.cancel_task('player', MatchType.STARTS_WITH)
                        self.controller.run_task('level/1_6', _next_level_task())
                        await asyncio.sleep(0.2)
                        continue

                if self.controller.is_running('player', MatchType.STARTS_WITH):
                    await asyncio.sleep(0.2)
                    continue
                self.controller.run_task('player', player_task(self.macro_groups[level - 1]))
                await asyncio.sleep(0.2)

        except asyncio.CancelledError:
            raise
