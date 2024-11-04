from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from src.data.command_model import CommandModel


@dataclass_json
@dataclass
class MacroRowModel:
    name: str
    count: int
    interval: float
    run: bool
    commands: list[CommandModel]
    is_point: bool = field(default=False)
    point: tuple[int, int] = field(default=(0, 0))


@dataclass_json
@dataclass
class MacroGroupModel:
    name: str
    macros: list[MacroRowModel]
