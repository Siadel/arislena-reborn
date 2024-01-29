import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord.bot_base import BotBase
from py_system.global_ import main_db, name_regex, game_settings
from py_system.tableobj import Faction

class TerritoryCommand(GroupCog, name="영토"):

    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name = "정찰",
        description = "미지의 영토를 정찰합니다. 악마들과 마주칠 것입니다! 승리하면 영토를 획득합니다."
    )
    async def scout(self, interaction: discord.Interaction):
        pass

async def setup(bot: BotBase):
    await bot.add_cog(TerritoryCommand(bot), guilds=bot.objectified_guilds)