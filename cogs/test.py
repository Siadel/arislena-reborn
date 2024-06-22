import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord.bot_base import BotBase
from py_discord import views, modals

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
        name="유저정보",
        description="유저 정보를 확인합니다."
    )
    async def user_info_test(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(title="유저 정보", color=discord.Color.green())
        embed.add_field(name="아이디(id)", value=member.id)
        embed.add_field(name="이름(name)", value=member.name)
        embed.add_field(name="보이는 닉네임(display name)", value=member.display_name)
        embed.add_field(name="닉네임(nick)", value=member.nick)
        embed.add_field(name="디스코드 가입일(created at)", value=member.created_at)
        embed.add_field(name="서버 가입일(joined at)", value=member.joined_at)
        await interaction.response.send_message(embed=embed)

async def setup(bot: BotBase):
    await bot.add_cog(CommandTest(bot))