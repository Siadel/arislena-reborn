import discord
from discord.ext.commands import GroupCog
from discord import app_commands, Colour
from datetime import datetime

from py_base import utility
from py_system._global import main_db, setting_by_guild
from py_system.tableobj import User
from py_discord import checks, embeds, views, warnings
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

        # 이미 등록되어 있는지 확인
        if checks.user_exists(interaction): raise warnings.AlreadyRegistered()
        
        user = User(
            discord_id=interaction.user.id, 
            discord_name=interaction.user.name, 
            register_date=datetime.now().strftime(utility.DATE_EXPRESSION))
        user.set_database(main_db)
        user.push()

        # 유저에게 "주인"이라는 이름의 역할 부여
        # id로 말고 이름으로 찾아야 함
        role = discord.utils.get(interaction.guild.roles, id=setting_by_guild.user_role_id[str(interaction.guild.id)])
        await interaction.user.add_roles(role)

        # settings.json에 있는 announce_channel_id로 메세지를 보냄
        await self.bot.announce(
            f"{interaction.user.mention} (*@{interaction.user.name}*)님께서 아리슬레나에 등록하셨습니다!",
            interaction.guild.id)

        # 등록 신청 완료 엠베드 출력
        # id, 이름, 등록일 출력

        await interaction.response.send_message(embed=embeds.register(user), ephemeral=True)

    @app_commands.command(
        name = "열람",
        description = "유저 정보를 열람합니다. 인자가 없을 경우 자신의 정보를 열람합니다."
    )
    @app_commands.describe(
        view_other_member = "다른 유저의 정보를 열람할 수 있는 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다.",
    )
    async def info(self, interaction: discord.Interaction, view_other_member:bool = False):
        
        if view_other_member:

            # 유저 정보 가져오기
            user_data_list = main_db.fetch_all("user")
            user_list = [User.from_data(data) for data in user_data_list]
            
            await interaction.response.send_message(
                "유저 정보 열람", 
                view=views.LookupView(
                    user_list,
                    button_class=views.UserLookupButton,
                    bot=self.bot,
                    interaction=interaction)
            )
        
        else:

            if not checks.user_exists(interaction): raise warnings.NotRegistered(interaction.user.name)
            user = User.from_database(main_db, discord_id=interaction.user.id)
        
            await interaction.response.send_message(
                embed=embeds.table_info(
                    discord.Embed(title=f"{interaction.user.display_name}님의 정보", color=Colour.green()), 
                    user
                )
            )

    @app_commands.command(
        name = "동기화",
        description = "아리슬레나의 데이터를 디스코드에 동기화합니다. | 동기화 데이터: 닉네임"
    )
    @app_commands.check(checks.user_exists)
    async def sync(self, interaction: discord.Interaction):
        # 유저 정보 가져오기
        user = User.from_database(main_db, discord_id=interaction.user.id)
        
        # 닉네임 동기화
        if user.discord_name != interaction.user.name:
            user.discord_name = interaction.user.name
            user.push()
        
        # 동기화 완료 엠베드 출력
        await interaction.response.send_message(
            f"{interaction.user.mention}님의 정보를 동기화했습니다.",
            embed=embeds.table_info(
                discord.Embed(title=f"{interaction.user.display_name}님의 정보", color=Colour.green()),
                user
            )
        )
    
    @app_commands.command(
        name = "등록해제",
        description = "[관리자 전용] 유저를 아리슬레나에서 등록 해제합니다."
    )
    @app_commands.describe(
        target_member = "등록 해제할 유저"
    )
    @app_commands.check(checks.is_admin)
    async def unregister(self, interaction: discord.Interaction, target_member:discord.Member):
        # if not check.is_admin(interaction.user):
        #     raise warning.NotAdmin()
        target_user = User.from_database(main_db, discord_id=target_member.id)
        if not target_user: raise warnings.NotRegistered(target_member.name)
        # 데이터에서 유저 삭제
        main_db.delete_with_id("user", target_user.id)
        # 유저에게 "주인"이라는 이름의 역할 삭제
        await target_member.remove_roles(
            discord.utils.get(interaction.guild.roles, id=setting_by_guild.user_role_id[str(interaction.guild.id)])
        )
        
        await interaction.response.send_message(f"**{target_member.display_name}**님을 아리슬레나에서 등록 해제했습니다.", ephemeral=True)
        await self.bot.announce(f"**{target_member.display_name}**님이 아리슬레나에서 등록 해제되었습니다.", interaction.guild.id)
        

async def setup(bot: BotBase):
    await bot.add_cog(UserManagement(bot), guilds=bot.objectified_guilds)