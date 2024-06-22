from py_discord.bot_base import BotBase, ServerManager
from py_base.jsonobj import BotSetting
from py_base.dbmanager import DatabaseManager

bot_setting = BotSetting.from_json_file()

ServerManager(
    BotBase(),
    bot_setting,
    DatabaseManager("main_test"),
    bot_setting.main_guild_id
)