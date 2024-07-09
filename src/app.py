import time

from pytorch.machine import Machine
from src.module.bot import Bot
from src.module.macro.bot import MacroBot
from src.module.signal import Signal
from src.module.switch import Switch
from src.data.data import Data
from src import config
from src.gui.gui import GUI
from src.module.looper import Looper
from src.module.window import WindowTool


def cleanup():
    # config.macro_bot.stop()
    config.signal.unhook()


def run():
    try:

        config.data = Data()

        signal = Signal()
        signal.hook()
        config.signal = signal

        config.switch = Switch()
        config.window_tool = WindowTool()

        config.looper = Looper()

        # config.machine = Machine()
        # config.machine.startup()

        # bot = Bot()
        # bot.start()
        # while not bot.ready:
        #     time.sleep(0.01)
        # config.bot = bot

        # macro_bot = MacroBot()
        # config.macro_bot = macro_bot

        gui = GUI()
        gui.start()
    finally:
        cleanup()
