import time

from src.module.bot import Bot
from src.module.macro.bot import MacroBot
from src.module.switch import Switch
from src.data.data import Data
from src import config
from src.gui.gui import GUI


def run():

    config.data = Data()

    config.switch = Switch()

    # bot = Bot()
    # bot.start()
    # while not bot.ready:
    #     time.sleep(0.01)
    # config.bot = bot

    macro_bot = MacroBot()
    config.macro_bot = macro_bot

    gui = GUI()
    gui.start()

    # switch.thread.join()
    # bot.thread.join()




