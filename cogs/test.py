import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord.bot_base import AriBot
from py_discord import views, modals
from py_discord.checks import is_admin

class CommandTest(GroupCog, name="테스트"):
    def __init__(self, bot: AriBot):
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name = "버튼",
        description = "버튼을 테스트합니다."
    )
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("버튼을 눌러봐!", view=views.test_button())

    @app_commands.command(
        name = "선택지",
        description = "선택지를 테스트합니다."
    )
    async def test2(self, interaction: discord.Interaction):
        await interaction.response.send_message("선택지를 선택해봐!", view=views.test_select())

    @app_commands.command(
        name = "모달",
        description = "모달을 테스트합니다."
    )
    async def test3(self, interaction: discord.Interaction):
        await interaction.response.send_modal(modals.ModalTest())

async def setup(bot: AriBot):
    await bot.add_cog(CommandTest(bot), guilds=bot._guild_list)