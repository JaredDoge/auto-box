# 開關
from pytorch.machine import Machine
from src.module.signal import Signal
from src.module.switch import Switch
from src.module.looper import Looper
from src.module.window import WindowTool

# 開關
switch: Switch | None = None
# 訊號監聽
signal: Signal | None = None
# 執行任務的thread looper
looper: Looper | None = None
# 視窗工具
window_tool: WindowTool | None = None
#
machine: Machine | None = None

# macro_bot: MacroBot | None = None

# G器人
bot = None

data = None

