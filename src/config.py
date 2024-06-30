# 開關
from src.module.macro.bot import MacroBot
from src.module.signal import Signal
from src.module.switch import Switch
from src.module.task_executor import Looper
from src.module.window import WindowTool

# 開關
switch: Switch | None = None
# 訊號監聽
signal: Signal | None = None

macro_bot: MacroBot | None = None

task_executor: Looper | None = None

window_tool: WindowTool | None = None


# G器人
bot = None

data = None

