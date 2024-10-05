from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class DependTargetModel:
    attr1: str
    attr2: str
    attr3: str


@dataclass_json
@dataclass
class DependModel:
    name: str
    targets: list[DependTargetModel] = field(default_factory=list)


@dataclass_json
@dataclass
class RescueSettingModel:
    rescue: bool
    setting: str


@dataclass_json
@dataclass
class AttrModel:
    name: str
    path: str
