from dataclasses import dataclass
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


@dataclass_json
@dataclass
class MacroGroupModel:
    name: str
    macros: list[MacroRowModel]
