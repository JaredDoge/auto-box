import os
from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from src.data.depend_model import DependModel, RescueSettingModel, AttrModel
from src.data.macro_model import MacroGroupModel
from src.data.rune_model import RuneSettingModel


@dataclass_json
@dataclass
class BaseModel:
    app: str = 'MapleStory'
    threshold: float = 0.985


class Data:

    def __init__(self):
        self._depend_attrs = self._to_dataclass(self.load_json("depend_attrs.json"), AttrModel)
        self._depend_bot = self._to_dataclass(self.load_json("depend_bot.json"), DependModel)
        self._depend_rescue_setting = self._to_dataclass(self.load_json("depend_rescue_setting.json", '{}'),
                                                         RescueSettingModel, many=False)
        self._macro_groups = self._to_dataclass(self.load_json("macro_groups.json"), MacroGroupModel)
        self._rune_setting = self._to_dataclass(self.load_json("rune_setting.json", '{}'), RuneSettingModel, many=False)
        self._base = self._to_dataclass(self.load_json("base.json", '{}'), BaseModel, many=False)
        self._forest_steps = self._to_dataclass(self.load_json("forest_steps.json"), MacroGroupModel) if os.path.exists(
            "forest_steps.json") else self._get_default_forest_steps()
        self.set_base(self._base)

    @staticmethod
    def load_json(config_file, d='[]'):
        if os.path.exists(config_file):
            with open(config_file, "r", encoding='utf-8') as file:
                data = file.read()
                return data
        else:
            return d

    @staticmethod
    def _to_dataclass(data: str, d_type: object, many=True) -> List:
        return d_type.schema().loads(data, many=many)

    @staticmethod
    def _to_json(data: object, d_type: object, many=True) -> str:
        return d_type.schema().dumps(data, ensure_ascii=False, many=many, indent=4)

    def _get_default_forest_steps(self):
        return [MacroGroupModel(name='進副本前', macros=[]), MacroGroupModel(name='第一關', macros=[]),
                MacroGroupModel(name='第二關', macros=[]), MacroGroupModel(name='第三關', macros=[]),
                MacroGroupModel(name='第四關', macros=[]), MacroGroupModel(name='第五關', macros=[]),
                MacroGroupModel(name='第六關', macros=[]), MacroGroupModel(name='第七關', macros=[])]

    def set_depend_attrs(self, attrs):
        self._depend_attrs = attrs
        with open("depend_attrs.json", "w", encoding='utf-8') as json_file:
            json_file.write(self._to_json(attrs, AttrModel))

    def set_depend_bot(self, depend_bot):
        self._depend_bot = depend_bot
        with open("depend_bot.json", "w", encoding='utf-8') as json_file:
            json_file.write(self._to_json(depend_bot, DependModel))

    def set_macro_groups(self, macro_groups):
        self._macro_groups = macro_groups
        with open("macro_groups.json", "w", encoding='utf-8') as json_file:
            json_file.write(self._to_json(macro_groups, MacroGroupModel))

    def set_depend_rescue_setting(self, setting):
        self._depend_rescue_setting = setting
        with open("depend_rescue_setting.json", "w", encoding='utf-8') as json_file:
            json_file.write(self._to_json(setting, RescueSettingModel, many=False))

    def set_base(self, base):
        self._base = base
        with open("base.json", "w", encoding='utf-8') as json_file:
            json_file.write(self._to_json(base, BaseModel, many=False))

    def set_rune_setting(self, setting):
        self._rune_setting = setting
        with open("rune_setting.json", "w", encoding='utf-8') as json_file:
            json_file.write(self._to_json(setting, RuneSettingModel, many=False))

    def set_forest_steps(self, forest_steps):
        self._forest_steps = forest_steps
        with open("forest_steps.json", "w", encoding='utf-8') as json_file:
            json_file.write(self._to_json(forest_steps, MacroGroupModel))

    def get_depend_rescue_setting(self):
        return self._depend_rescue_setting

    def get_depend_attrs(self):
        return self._depend_attrs

    def get_depend_bot(self):
        return self._depend_bot

    def get_macro_groups(self):
        return self._macro_groups

    def get_base(self):
        return self._base

    def get_rune_setting(self):
        return self._rune_setting

    def get_forest_steps(self):
        return self._forest_steps
