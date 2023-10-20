import discord
from discord.ext.commands import GroupCog
from discord import app_commands
from datetime import datetime

from py_base import utility
from py_system import tableobj
from py_system.database import MainDB
from py_discord.bot_base import BotBase

class UserManagement(GroupCog, name="유저"):
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name = "등록",
        description = "아리슬레나에 등록합니다."
    )
    async def register(self, interaction: discord.Interaction):

        db = MainDB()

        user:tableobj.User = db.fetch("user", f"discord_id = {interaction.user.id}")
        if user is not None:
            embed_title = "등록 정보"
            embed_description = "이미 등록했습니다."
            embed_color = discord.Colour.blue()
        else:
            embed_title = "환영합니다!"
            embed_description = "다음 정보가 저장되었습니다."
            embed_color = discord.Colour.green()
            user = tableobj.User(0, interaction.user.id, interaction.user.name, datetime.now().strftime(utility.DATE_EXPRESSION))
            db.insert(user)
        # 등록 신청 완료 엠베드 출력
        # id, 이름, 등록일 출력
        embed = discord.Embed(title=embed_title, description=embed_description, color=embed_color)
        embed.add_field(name = "디스코드 아이디", value = interaction.user.id)
        embed.add_field(name = "유저네임", value = interaction.user.name)
        embed.add_field(name = "등록일", value = user.register_date)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        

async def setup(bot: BotBase):
    await bot.add_cog(UserManagement(bot), guilds=bot.objectified_guilds)