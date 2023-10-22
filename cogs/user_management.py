import discord
from discord.ext.commands import GroupCog
from discord import app_commands
from datetime import datetime

from py_base import utility
from py_system import tableobj, jsonobj
from py_system.database import main_db
from py_discord import warning, embed, view
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

        user:tableobj.User = main_db.fetch("user", f"discord_id = {interaction.user.id}")

        if user:
            raise warning.AlreadyRegistered()
        
        user = tableobj.User(
            discord_id=interaction.user.id, 
            discord_name=interaction.user.name, 
            register_date=datetime.now().strftime(utility.DATE_EXPRESSION))
        user_settings = tableobj.User_setting(0, interaction.user.id)
        main_db.insert(user)
        main_db.insert(user_settings)

        # 유저에게 "주인"이라는 이름의 역할 부여
        # id로 말고 이름으로 찾아야 함
        role = discord.utils.get(interaction.guild.roles, name="주인")
        await interaction.user.add_roles(role)

        # settings.json에 있는 announce_channel_id로 메세지를 보냄
        settings = jsonobj.Settings()
        channel = self.bot.get_channel(settings.announce_channel_id)

        nickname = interaction.user.nick if interaction.user.nick else "닉네임 없음"
        await channel.send(f"{interaction.user.global_name}(@{interaction.user.name}, {nickname})님께서 아리슬레나에 등록하셨습니다!")

        # 등록 신청 완료 엠베드 출력
        # id, 이름, 등록일 출력

        await interaction.response.send_message(embed=embed.register(user), ephemeral=True)

    @app_commands.command(
        name = "설정",
        description = "유저 설정을 확인하고 변경 가능한 ui를 출력합니다."
    )
    async def setting(self, interaction: discord.Interaction):
        # 유저가 등록되었는지 확인 후, 등록되지 않았으면 등록을 요청
        user:tableobj.User = main_db.fetch("user", f"discord_id = {interaction.user.id}")
        if user is None: raise warning.NotRegistered()
        # user_setting을 main_db에서 가져오고 view 만들기

        user_setting = main_db.fetch("user_setting", f"discord_id = {interaction.user.id}")

        v = view.user_setting_view(user_setting)
        await interaction.response.send_message(view=v, ephemeral=True)
        

async def setup(bot: BotBase):
    await bot.add_cog(UserManagement(bot), guilds=bot.objectified_guilds)