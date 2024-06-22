import discord
from discord.ext.commands import GroupCog
from discord import app_commands, Interaction

from py_discord.bot_base import BotBase
from py_discord.modals import TrainLivestockModal
from py_base.ari_enum import ResourceCategory

class LivestockCommand(GroupCog, name="가축"):
    
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()
        
    @app_commands.command(
        name = "차출",
        description = f"세력이 보유한 {ResourceCategory.LIVESTOCK.express()}자원을 노동에 활용할 수 있게 만듭니다."
    )
    async def train_livestock(self, interaction: Interaction):
        
        interaction.response.send_modal(TrainLivestockModal(bot=self.bot))


async def setup(bot: BotBase):
    await bot.add_cog(LivestockCommand(bot))