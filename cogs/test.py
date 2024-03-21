import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord.bot_base import BotBase, schedule_manager, main_db
from py_discord import views, modals
from py_discord.checks import is_admin

class CommandTest(GroupCog, name="테스트"):
    def __init__(self, bot: BotBase):
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
    
    @app_commands.command(
        name = "턴넘기기",
        description = "턴을 넘깁니다. ⚠ 프리시즌 테스트 기간이거나, 기능 테스트 목적이 아니면 비상 시에만 사용해야 합니다."
    )
    @app_commands.check(is_admin)
    async def elapse_turn(self, interaction: discord.Interaction):
        schedule_manager.end_turn()
        await interaction.response.send_message(f"턴이 넘어갔습니다. (현재 턴: {schedule_manager.schedule.now_turn})")

async def setup(bot: BotBase):
    await bot.add_cog(CommandTest(bot), guilds=bot.objectified_guilds)