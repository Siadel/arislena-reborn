from py_discord.bot_base import BotBase, ServerManager
from py_system._global import bot_setting
from py_base.dbmanager import DatabaseManager

ServerManager(
    BotBase(bot_setting),
    bot_setting,
    DatabaseManager("main_test"),
    bot_setting.main_guild_id
)