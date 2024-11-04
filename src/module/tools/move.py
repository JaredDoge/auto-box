import asyncio
import time
from dataclasses import asdict
from enum import Enum

import keyboard

from src import config
from src.module import screen
from src.module.log import log
from src.module.looper import TaskController
from src.module.tools import mini_map


class MoveModel(Enum):
    WALK = 1
    DOUBLE_JUMP = 2


class Cooldown:
    def __init__(self, cooldown_time):
        """初始化冷卻時間，單位為秒"""
        self.cooldown_time = cooldown_time  # 冷卻時間
        self.last_used_time = 0  # 上一次使用的時間

    def is_ready(self):
        """檢查是否已經過了冷卻時間"""
        current_time = time.time()
        return (current_time - self.last_used_time) >= self.cooldown_time

    def reset(self):
        """重置冷卻時間，設置上一次使用時間為當前時間"""
        self.last_used_time = time.time()

    def use_if_ready(self, action):
        """如果冷卻完成則執行動作，並重置冷卻"""
        if self.is_ready():
            action()  # 執行傳入的動作
            self.reset()  # 重置冷卻時間

    async def use_if_ready_async(self, action):
        """如果冷卻完成則執行異步動作，並重置冷卻"""
        if self.is_ready():
            await action()  # 執行傳入的異步動作
            self.reset()  # 重置冷卻時間


class Move:
    def __init__(self, controller: TaskController):
        self.controller = controller
        self.keys = asdict(config.data.get_rune_setting())

    async def go_point(self, point, mode: MoveModel = MoveModel.DOUBLE_JUMP, tolerance=1):
        def _release_all():
            for value in self.keys.values():
                _release(value)

        def _release(key):
            keyboard.release(key)

        def _press(key):
            keyboard.press(key)

        async def _click(key, sleep=0.05):
            _press(key)
            await asyncio.sleep(sleep)
            _release(key)

        def _go_right():
            _release(self.keys['left'])
            _press(self.keys['right'])

        def _go_left():
            _release(self.keys['right'])
            _press(self.keys['left'])

        async def _rope():
            _release(self.keys['right'])
            _release(self.keys['left'])
            await _click(self.keys['rope'])
            await asyncio.sleep(2)

        async def _jump_off():
            _release(self.keys['right'])
            _release(self.keys['left'])
            await _click(self.keys['jump_off'])
            await asyncio.sleep(1.5)

        # 檢測角色x軸是否卡住
        def is_x_axis_stuck():
            if len(previous_positions) < 3:
                return False  # 需要至少三幀的數據進行比較
                # 比較最近三幀的坐標是否相同
            return all(pos == previous_positions[0] for pos in previous_positions)

        # 檢測角色y軸是否卡住
        def is_y_axis_stuck():
            if len(previous_positions) < 3:
                return False  # 需要至少三幀的數據進行比較
                # 比較最近三幀的坐標是否相同
            return all(pos == previous_positions[1] for pos in previous_positions)

        async def _to_rune_x():

            def _double_jump():
                async def j():
                    try:
                        await _click(self.keys['jump'], 0.1)
                        await asyncio.sleep(0.05)
                        await _click(self.keys['jump'], 0.1)
                    except asyncio.CancelledError:
                        raise

                self.controller.run_task('d_j', j())

            distance = abs(player_x - point_x)
            if distance <= tolerance:
                return True

            if player_x > point_x:
                _go_left()
            elif player_x < point_x:
                _go_right()

            if mode == MoveModel.DOUBLE_JUMP and distance > 20:
                double_jump_cd.use_if_ready(_double_jump)

            if is_x_axis_stuck():
                # x軸卡住了
                jump_cd.use_if_ready(lambda: keyboard.send(self.keys['jump']))

            return False

        async def _to_rune_y():
            if abs(player_y - point_y) <= tolerance:
                return True
            elif player_y > point_y:
                await _rope()
            elif player_y < point_y:
                await _jump_off()
            return False

        previous_positions = []
        jump_cd = Cooldown(1)
        double_jump_cd = Cooldown(1)
        try:
            while True:
                full = await config.window_tool.wait_game_screen()

                mm = mini_map.find_minimap(full)
                if mm is None:
                    log('找不到小地圖')
                    await asyncio.sleep(0.2)
                    continue

                while True:
                    full = await config.window_tool.wait_game_screen()
                    minimap = screen.cut_by_tl_br(full, mm)
                    player = mini_map.find_player2(minimap)
                    if not player:
                        log('找不到人物')
                        await asyncio.sleep(0.2)
                        continue

                    player_x, player_y = player
                    point_x, point_y = point

                    previous_positions.append(player)
                    # 限制過去的記錄數量，保持最近的三幀
                    if len(previous_positions) > 3:
                        previous_positions.pop(0)

                    if not await _to_rune_x():
                        await asyncio.sleep(0.2)
                        continue

                    if not await _to_rune_y():
                        await asyncio.sleep(0.2)
                        continue
                    return
        except asyncio.CancelledError:
            raise
        finally:
            _release_all()
