from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class RuneSettingModel:
    right: str
    left: str
    up: str
    down: str
    jump_off: str
    jump: str
    rope: str
    collect: str
