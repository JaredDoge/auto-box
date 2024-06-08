from dataclasses import dataclass, field
from typing import List, Union, Optional, TypeAlias
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class SignalModelBase:
    signal: str


@dataclass_json
@dataclass
class DelaySignalModel(SignalModelBase):
    signal: str = field(init=False, default='delay')
    time: float


@dataclass_json
@dataclass
class KeyboardSignalModel(SignalModelBase):
    signal: str = field(init=False, default='keyboard')
    event_type: str
    event_name: str


SignalModel: TypeAlias = Union[DelaySignalModel, KeyboardSignalModel]
