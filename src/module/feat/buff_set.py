from typing import Dict
import asyncio
import time
import json
from datetime import timedelta
import keyboard

from src.module.log import log


class BuffSet:
    _instance = None  # 用于存储单例实例

    @classmethod
    def get(cls, json_path: str = "buff.json"):
        if not cls._instance:
            cls._instance = cls(json_path)
        return cls._instance

    def __init__(self, json_path: str = "buff.json"):
        if BuffSet._instance is not None:
            raise Exception("This is a singleton class. Use BuffSet.get() to access the instance.")

        # 初始化 BuffSet
        self.buff_data: Dict[str, float] = {}  # 儲存buff按鍵和CD時間，單位是秒
        self.last_used: Dict[str, float] = {}  # 儲存每個buff最後使用的時間
        self.json_path = json_path
        self.load_buff_data()

    def load_buff_data(self) -> None:
        """從JSON檔案讀取buff設定"""
        try:
            with open(self.json_path, 'r') as f:
                self.buff_data = json.load(f)
            # 初始化最後使用時間為0
            for key in self.buff_data:
                self.last_used[key] = 0
        except FileNotFoundError:
            print(f"找不到檔案: {self.json_path}")
        except json.JSONDecodeError:
            print(f"JSON格式錯誤: {self.json_path}")

    async def check(self) -> None:
        """
        檢查所有buff是否已經超過CD時間，如果是則按順序發送按鍵事件
        """
        try:
            for key, cd_time in self.buff_data.items():
                current_time = time.time()
                # 首次只記錄時間，不按下buff，第一次自己按
                if self.last_used[key] == 0:
                    log(f"buff: {key} 首次不使用")
                    self.last_used[key] = current_time
                    continue
                # 檢查是否超過CD時間
                elapsed_time = current_time - self.last_used[key]
                if elapsed_time >= cd_time:
                    # 發送按鍵事件
                    keyboard.send(key)
                    log(f"使用buff: {key}")
                    # 更新最後使用時間
                    self.last_used[key] = current_time
                    # 等待一小段時間，避免按鍵太快
                    await asyncio.sleep(1)
                else:
                    remaining_time = cd_time - elapsed_time
                    log(f"buff: {key} 還在CD，剩: {str(timedelta(seconds=int(remaining_time)))}")
        except asyncio.CancelledError:
            raise
