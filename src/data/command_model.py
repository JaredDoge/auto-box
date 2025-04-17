from dataclasses import dataclass, field
from typing import TypeAlias, Union, Literal
from marshmallow import fields
from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass
class CommandModelBase:
    command: str


@dataclass_json
@dataclass
class DelayCommandModel(CommandModelBase):
    command: str = field(init=False, default='delay')
    type: Literal['time', 'border'] = field(
        default='time',
        metadata=config(
            mm_field=fields.String(validate=lambda x: x in ['time', 'border'])
        )
    )  # 預設為時間延遲，兼容舊版格式
    time: float = 0.0  # Used when type is 'time'
    operator: str = ''  # Used when type is 'border' (lt, lte, eq, gte, gt)
    ratio: int = 0  # Used when type is 'border'


@dataclass_json
@dataclass
class KeyboardCommandModel(CommandModelBase):
    command: str = field(init=False, default='keyboard')
    event_type: str
    event_name: str


CommandModel: TypeAlias = Union[DelayCommandModel, KeyboardCommandModel]
