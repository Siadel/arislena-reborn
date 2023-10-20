import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord.bot_base import BotBase
from py_discord import view

class CommandTest(GroupCog, name="테스트"):
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()

    @app_commands.command(
            name = "버튼",
            description = "버튼을 테스트합니다."
    )
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("버튼을 눌러봐!", view=view.test_button())

    @app_commands.command(
            name = "선택지",
            description = "선택지를 테스트합니다."
    )
    async def test2(self, interaction: discord.Interaction):
        await interaction.response.send_message("선택지를 선택해봐!", view=view.test_select_view())

async def setup(bot: BotBase):
    await bot.add_cog(CommandTest(bot), guilds=bot.objectified_guilds)