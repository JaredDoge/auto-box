from dataclasses import dataclass, field
from typing import TypeAlias, Union

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CommandModelBase:
    command: str


@dataclass_json
@dataclass
class HorizontalBorderCommandModel(CommandModelBase):
    command: str = field(init=False, default='horizontal_border')
    operator: str
    ratio: float


@dataclass_json
@dataclass
class DelayCommandModel(CommandModelBase):
    command: str = field(init=False, default='delay')
    time: float


@dataclass_json
@dataclass
class KeyboardCommandModel(CommandModelBase):
    command: str = field(init=False, default='keyboard')
    event_type: str
    event_name: str


CommandModel: TypeAlias = Union[DelayCommandModel, KeyboardCommandModel, HorizontalBorderCommandModel]
