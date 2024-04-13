import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord.bot_base import BotBase

class LivestockCommand(GroupCog, name="가축"):
    
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()


async def setup(bot: BotBase):
    await bot.add_cog(LivestockCommand(bot))