import os
from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json
from src.module.cv import cv_imread


@dataclass_json
@dataclass
class BaseModel:
    app: str = 'MapleStory'
    threshold: float = 0.985


@dataclass_json
@dataclass
class SettingModel:
    rescue: bool = False


@dataclass_json
@dataclass
class AttrModel:
    name: str
    path: str


@dataclass_json
@dataclass
class TargetAttrModel:
    attr1: str
    attr2: str
    attr3: str


@dataclass_json
@dataclass
class TabModel:
    name: str
    targets: list[TargetAttrModel] = field(default_factory=list)


class Data:

    def __init__(self):
        self._attrs = self._to_dataclass(self.load_json("attrs.json"), AttrModel)
        self._tabs = self._to_dataclass(self.load_json("attach_tabs.json"), TabModel)
        self._setting = self._to_dataclass(self.load_json("setting.json", '{}'), SettingModel, many=False)
        self._base = self._to_dataclass(self.load_json("base.json", '{}'), BaseModel, many=False)
        self._templates = {a.name: cv_imread(a.path) for a in self._attrs if os.path.exists(a.path)}
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

    def set_attrs(self, attrs):
        self._attrs = attrs
        with open("attrs.json", "w",  encoding='utf-8') as json_file:
            json_file.write(self._to_json(attrs, AttrModel))

    def set_tabs(self, tabs):
        self._tabs = tabs
        with open("attach_tabs.json", "w",  encoding='utf-8') as json_file:
            json_file.write(self._to_json(tabs, TabModel))

    def set_setting(self, setting):
        self._setting = setting
        with open("setting.json", "w",  encoding='utf-8') as json_file:
            json_file.write(self._to_json(setting, SettingModel, many=False))

    def set_base(self, base):
        self._base = base
        with open("base.json", "w", encoding='utf-8') as json_file:
            json_file.write(self._to_json(base, BaseModel, many=False))

    def get_setting(self):
        return self._setting

    def get_attrs(self):
        return self._attrs

    def get_tabs(self):
        return self._tabs

    def get_templates(self):
        return self._templates

    def get_template(self, name):
        return self._templates[name]

    def get_base(self):
        return self._base
