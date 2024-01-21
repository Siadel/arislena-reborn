import discord
from discord.ext.commands import GroupCog
from discord import app_commands, Colour
from datetime import datetime

from py_base import utility
from py_system import tableobj, jsonobj
from py_system.ari_global import main_db
from py_discord import warning, embed, view, check
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

        user:tableobj.User = main_db.fetch("user", f"discord_ID = {interaction.user.id}")

        if user:
            raise warning.AlreadyRegistered()
        
        user = tableobj.User(
            discord_ID=interaction.user.id, 
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
        await self.bot.announce(
            f"**{interaction.user.display_name}** (*@{interaction.user.name}*)님께서 아리슬레나에 등록하셨습니다!",
            interaction.guild.id)

        # 등록 신청 완료 엠베드 출력
        # id, 이름, 등록일 출력

        await interaction.response.send_message(embed=embed.register(user), ephemeral=True)

    @app_commands.command(
        name = "설정",
        description = "유저 설정을 확인하고 변경 가능한 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다."
    )
    async def setting(self, interaction: discord.Interaction):
        # 유저가 등록되었는지 확인 후, 등록되지 않았으면 등록을 요청
        user:tableobj.User = main_db.fetch("user", f"discord_ID = {interaction.user.id}")
        if not user: raise warning.NotRegistered()
        # user_setting을 main_db에서 가져오고 view 만들기

        user_setting = main_db.fetch("user_setting", f"discord_ID = {interaction.user.id}")

        v = view.user_setting_view(user_setting)
        await interaction.response.send_message(view=v, ephemeral=True)

    @app_commands.command(
        name = "열람",
        description = "유저 정보를 열람합니다. 인자가 없을 경우 자신의 정보를 열람합니다."
    )
    @app_commands.describe(
        view_other_member = "다른 유저의 정보를 열람할 수 있는 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다.",
    )
    async def info(self, interaction: discord.Interaction, view_other_member:bool = False):
        
        if view_other_member:
            my_info = main_db.fetch("user", f"discord_ID = {interaction.user.id}")
            
            await interaction.response.send_message(
                embed=embed.table_info(discord.Embed(title=f"{interaction.user.display_name}님의 정보", color=Colour.green()), my_info))
            return
        
        await interaction.response.send_message(
            "유저 정보 열람", view=view.GeneralLookupView(
                main_db.fetch_all("user"), display_column="discord_name")
        )
        
    # @app_commands.command(
    #     name = "모두열람",
    #     description = "서버에 등록된 모든 유저의 정보를 열람합니다."
    # )
    # async def info_all(self, interaction: discord.Interaction):
    #     users:list[tableobj.User] = main_db.fetch_all("user")

    #     for idx, user in enumerate(users):
    #         ebd = embed.table_info(discord.Embed(title=f"**{interaction.user.display_name}**님의 정보", color=Colour.green()), user)

    #         if idx == 0:
    #             await interaction.response.send_message(embed=ebd, ephemeral=True)
    #         else:
    #             await interaction.followup.send(embed=ebd, ephemeral=True)
    
    @app_commands.command(
        name = "등록해제",
        description = "[관리자 전용] 유저를 아리슬레나에서 등록 해제합니다."
    )
    @app_commands.describe(
        target_member = "등록 해제할 유저"
    )
    @app_commands.check(check.is_admin)
    async def unregister(self, interaction: discord.Interaction, target_member:discord.Member):
        # if not check.is_admin(interaction.user):
        #     raise warning.NotAdmin()
        target_user:tableobj.User = main_db.fetch("user", f"discord_ID = {target_member.id}")
        target_user_setting:tableobj.User_setting = main_db.fetch("user_setting", f"discord_ID = {target_member.id}")
        if not target_user: raise warning.NotRegistered(target_member.name)
        # 데이터에서 유저, 유저 설정 삭제
        main_db.delete_with_id("user", target_user.ID)
        main_db.delete_with_id("user_setting", target_user_setting.ID)
        # 유저에게 "주인"이라는 이름의 역할 삭제
        await target_member.remove_roles(discord.utils.get(interaction.guild.roles, name="주인"))
        
        await interaction.response.send_message(f"**{target_member.display_name}**님을 아리슬레나에서 등록 해제했습니다.", ephemeral=True)
        await self.bot.announce(f"**{target_member.display_name}**님이 아리슬레나에서 등록 해제되었습니다.", interaction.guild.id)
        

async def setup(bot: BotBase):
    await bot.add_cog(UserManagement(bot), guilds=bot.objectified_guilds)