import discord
from discord.ext.commands import GroupCog
from discord import app_commands
from datetime import datetime

from py_base import utility
from py_system.tableobj import User
from py_discord import embeds, views
from py_discord.bot_base import BotBase
from py_base import warnings

class UserManagement(GroupCog, name="유저"):
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name = "등록",
        description = "아리슬레나에 등록합니다."
    )
    async def register(self, interaction: discord.Interaction):
        
        database = self.bot.get_database(interaction.guild_id)

        # 이미 등록되어 있는지 확인
        self.bot.check_user_not_exists_or_raise(interaction)
        
        user = User(
            discord_id=interaction.user.id, 
            discord_name=interaction.user.name, 
            register_date=datetime.now().strftime(utility.DATE_FORMAT))
        user.set_database(database)
        user.push()

        # 유저에게 "주인"이라는 이름의 역할 부여
        # id로 말고 이름으로 찾아야 함
        role = discord.utils.get(
            interaction.guild.roles,
            id=self.bot.get_server_manager(interaction.guild_id).guild_setting.user_role_id
        )
        await interaction.user.add_roles(role)

        # settings.json에 있는 announce_channel_id로 메세지를 보냄
        await self.bot.announce_channel(
            f"{interaction.user.mention} (*@{interaction.user.name}*)님께서 아리슬레나에 등록하셨습니다!",
            self.bot.get_server_manager(interaction.guild_id).guild_setting.announce_channel_id)

        # 등록 신청 완료 엠베드 출력
        # id, 이름, 등록일 출력

        await interaction.response.send_message(embed=embeds.register(user), ephemeral=True)
        
        database.connection.commit()

    @app_commands.command(
        name = "열람",
        description = "유저 정보를 열람합니다. 인자가 없을 경우 자신의 정보를 열람합니다."
    )
    @app_commands.describe(
        view_my_info = "내 정보를 열람하고 싶은 경우 True로 설정하세요.",
    )
    async def info(self, interaction: discord.Interaction, view_my_info:bool = False):
        
        if view_my_info:

            self.bot.check_user_exists_or_raise(interaction)
            user = User.from_database(self.bot.get_database(interaction.guild_id), discord_id=interaction.user.id)
        
            await interaction.response.send_message(
                embed=embeds.TableObjectEmbed(f"{interaction.user.display_name}님의 정보").add_basic_info(
                    user,
                    self.bot.get_server_manager(interaction.guild_id).table_obj_translator
                )
            )
        
        else:

            # 유저 정보 가져오기
            user_data_list = self.bot.get_database(interaction.guild_id).fetch_all("user")
            user_list = [User.from_data(data) for data in user_data_list]
            
            await interaction.response.send_message(
                "유저 정보 열람", 
                view=views.TableObjectView(
                    user_list,
                    sample_button=views.UserLookupButton(self.bot, interaction)
                )
            )
        

    @app_commands.command(
        name = "동기화",
        description = "아리슬레나 유저의 데이터(닉네임)를 디스코드에 동기화합니다."
    )
    async def sync(self, interaction: discord.Interaction):
        
        user = User.fetch_or_raise(self.bot.get_database(interaction.guild_id), warnings.NotRegistered(interaction.user.display_name), discord_id=interaction.user.id)
        
        # 닉네임 동기화
        if user.discord_name != interaction.user.name:
            user.discord_name = interaction.user.name
            user.push()
        
        # 동기화 완료 엠베드 출력
        await interaction.response.send_message(
            f"{interaction.user.mention}님의 정보를 동기화했습니다.",
            embed=embeds.TableObjectEmbed(f"{interaction.user.display_name}님의 정보").add_basic_info(
                user,
                self.bot.get_server_manager(interaction.guild_id).table_obj_translator
            )
        )
    
    @app_commands.command(
        name = "등록해제",
        description = "[관리자 전용] 유저를 아리슬레나에서 등록 해제합니다."
    )
    @app_commands.describe(
        target_member = "등록 해제할 유저"
    )
    async def unregister(self, interaction: discord.Interaction, target_member:discord.Member):
        self.bot.check_admin_or_raise(interaction)
        database = self.bot.get_database(interaction.guild_id)
        
        target_user = User.fetch_or_raise(database, warnings.NotRegistered(interaction.user.display_name), discord_id=interaction.user.id)
        
        # 데이터에서 유저 삭제
        database.delete_with_id("user", target_user.id)
        # 유저에게 "주인"이라는 이름의 역할 삭제
        await target_member.remove_roles(
            discord.utils.get(
                interaction.guild.roles, 
                id=self.bot.get_server_manager(interaction.guild_id).guild_setting.user_role_id
            )
        )
        
        await interaction.response.send_message(f"**{target_member.display_name}**님을 아리슬레나에서 등록 해제했습니다.", ephemeral=True)
        await self.bot.announce_channel(f"**{target_member.display_name}**님이 아리슬레나에서 등록 해제되었습니다.", self.bot.get_server_manager(interaction.guild_id).guild_setting.announce_channel_id)
        

async def setup(bot: BotBase):
    await bot.add_cog(UserManagement(bot))