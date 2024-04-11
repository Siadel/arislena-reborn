import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord.bot_base import AriBot

class LivestockCommand(GroupCog, name="가축"):
    
    def __init__(self, bot: AriBot):
        self.bot = bot
        super().__init__()


async def setup(bot: AriBot):
    await bot.add_cog(LivestockCommand(bot), guilds=bot._guild_list)