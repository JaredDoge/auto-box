import asyncio
import sys
import time
import traceback
from dataclasses import dataclass
from typing import Dict, TypedDict, Union, Callable, Tuple, List

import cv2
import keyboard
import mouse

from src import config
from src.data.depend_model import DependTargetModel
from src.data.macro_model import MacroRowModel
from src.module import screen, cv2_util
from src.module.depend import depend_util
from src.module.log import log, single
from enum import Enum


@dataclass
class Target:
    attr: str
    count: int


@dataclass
class BoxInfo:
    again_center: Tuple[int, int]  # 在使用一次 按鈕的 中心位置
    box_block: Tuple[Tuple[int, int], Tuple[int, int]]  # 方塊的範圍
    identify_block: Tuple[Tuple[int, int], Tuple[int, int]]  # 要辨識淺能的範圍


class DependExecutor:
    _INTERVAL = 1

    def __init__(self):
        self.looper = config.looper
        self.main_task: asyncio.Task | None = None
        self.stop_callback: Union[Callable, None] = None

    async def _cancel(self, task):
        if task is None:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def set_stop_callback(self, call):
        self.stop_callback = call

    def _find_box_info(self, left, top, full) -> BoxInfo | None:

        if depend_util.depend_exist(full):  # 珍貴附加
            box = depend_util.find_depend_box(full)
            if box is None:
                return None

            again = depend_util.find_depend_again_center(full)
            if again is None:
                return None

            return BoxInfo(box_block=box, again_center=(left + again[0], top + again[1]), identify_block=box)

        elif depend_util.recover_exist(full):
            box = depend_util.find_recover_box(full)
            if box is None:
                return None

            again = depend_util.find_recover_again_center(full)
            if again is None:
                return None

            identify = depend_util.find_recover_identify_block(full)
            if identify is None:
                return None

            return BoxInfo(box_block=box, again_center=(left + again[0], top + again[1]), identify_block=identify)

        else:
            return None

    async def _run(self, datas, templates):

        try:
            while not config.window_tool.is_foreground():
                await asyncio.sleep(1)
                config.window_tool.to_foreground()
                log('等待遊戲視窗中')

            full = await config.window_tool.get_game_screen()
            geo = config.window_tool.get_geometry()
            box = self._find_box_info(geo['left'], geo['top'], full)
            if box is None:
                log('沒開啟 附加框 或 不要有任何東西擋到附加框')
                self.stop()
                return
            # cv2.rectangle(full, box.box_block[0], box.box_block[1], (0, 255, 0), 2)
            # cv2.rectangle(full, box.identify_block[0], box.identify_block[1], (255,0 , 0), 2)
            # screen.show_frame(full)

            # 嘗試檢測附加框卡住秒數
            attempt = 5
            while True:
                full = await config.window_tool.get_game_screen()

                box_frame = depend_util.get_block_frame(full, box.box_block)

                # screen.show_frame(box_frame)

                # 檢查 在一次使用 有沒有卡住
                # if depend_util.find_depend_again_disable(box_frame):
                #     if attempt <= 0:  # 需要搶救
                #         log(f'檢測到附加框卡住，嘗試恢復')
                #         # await
                #     else:
                #         attempt -= 1
                #         await asyncio.sleep(1)
                #         continue
                # attempt = 5  # reset

                # 找 OK 按鈕
                if depend_util.ok_exist(box_frame):
                    keyboard.send('enter')
                    await asyncio.sleep(0.1)
                    continue

                identify_frame = depend_util.get_block_frame(full, box.identify_block)

                # 等 傳說 出現
                if not depend_util.legend_exist(identify_frame):
                    await asyncio.sleep(0.2)
                    continue
                # 開始辨識前確保滑鼠不在辨識範圍
                x, y = box.again_center
                mouse.move(x, y)  # 移到在使用一次

                # 開始辨識
                lucky = False

                single('=============START=============')
                for data in datas:
                    lucky = self._find_target(identify_frame, templates, data)
                    if lucky:
                        break
                single('==============END==============')

                if lucky:
                    log(f'目標達成')
                    self.stop()
                    return

                # 沒找到
                x, y = box.again_center
                mouse.move(x, y)  # 移到在使用一次

                mouse.press(mouse.LEFT)
                await asyncio.sleep(0.05)
                mouse.release(mouse.LEFT)

                await asyncio.sleep(0.2)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=None, file=sys.stdout)
            self.stop()

    def _find_target(self, frame, templates, targets: List[Target]) -> bool:
        all_equal = True
        single('-')
        for target in targets:
            find_count = len(
                cv2_util.unique(frame, templates[target.attr], 0.985))
            single(f'{target.attr}:目標{target.count},找到{find_count}')
            if find_count != target.count:
                all_equal = False
        single('-')
        return all_equal

    def _convert(self, target_attr: DependTargetModel) -> List[Target]:
        attr_counts = {}
        for attr_name in ["attr1", "attr2", "attr3"]:
            attr_value = getattr(target_attr, attr_name)

            if attr_value == '空':
                continue

            if attr_value in attr_counts:
                attr_counts[attr_value] += 1
            else:
                attr_counts[attr_value] = 1
        result_models = [Target(attr=attr, count=count) for attr, count in attr_counts.items()]
        return result_models

    def start(self, data: list[DependTargetModel]):
        async def _start():
            converted_data: List[List[Target]] = [self._convert(item) for item in data]
            templates = depend_util.get_attr_template(config.data.get_depend_attrs())
            self.main_task = self.looper.run_task(self._run(converted_data, templates))

        self.looper.run(_start())

    def stop(self):
        async def _stop():
            await self._cancel(self.main_task)
            self.main_task = None

            if self.stop_callback:
                self.stop_callback()

        self.looper.run(_stop())
