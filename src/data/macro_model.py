from dataclasses import dataclass, field
from typing import List, Union, Optional, TypeAlias
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CommandModelBase:
    command: str


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


CommandModel: TypeAlias = Union[DelayCommandModel, KeyboardCommandModel]


@dataclass_json
@dataclass
class MacroRowModel:
    name: str
    count: int
    interval: int
    commands: list[CommandModel]


@dataclass_json
@dataclass
class MacroGroupModel:
    name: str
    macros: list[MacroRowModel]
