import discord
from discord.ext.commands import GroupCog
from discord import app_commands, Colour

from py_discord.bot_base import BotBase


class GuildManagement(GroupCog, name="서버설정"):
    
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()
        
    @app_commands.command(
        name = "열람",
        description = "서버 설정을 열람합니다."
    )
    async def show(self, interaction: discord.Interaction):
        server_manager = self.bot.get_server_manager(interaction.guild_id)
        
        def get_mention_or_default(obj: discord.Role | discord.TextChannel):
            if obj is None:
                return "설정되지 않음"
            return obj.mention
        
        result_embed = discord.Embed(
            title="서버 설정",
            color=Colour.green()
        )
        result_embed.add_field(
            name="유저 역할", 
            value=get_mention_or_default(
                discord.utils.get(interaction.guild.roles, id=server_manager.guild_setting.user_role_id)
            )
        )
        result_embed.add_field(
            name="관리자 역할", 
            value=get_mention_or_default(
                discord.utils.get(interaction.guild.roles, id=server_manager.guild_setting.admin_role_id)
            )
        )
        result_embed.add_field(
            name="공지 채널", 
            value=get_mention_or_default(
                discord.utils.get(interaction.guild.text_channels, id=server_manager.guild_setting.announce_channel_id)
            )
        )
        
        await interaction.response.send_message(embed=result_embed)
        
    @app_commands.command(
        name = "변경",
        description = "[서버 administrator 권한 필요] 아리에게 게임 실행에 필요한 '유저'와 '관리자' 역할과, '시스템 메세지 채널'을 설정합니다."
    )
    @app_commands.describe(
        user_role = "'유저'로 지정할 역할",
        admin_role = "'관리자'로 지정할 역할",
        announce_channel = "아리가 시스템 메세지(턴 종료/시작 보고 등)를 보낼 채널"
    )
    @app_commands.check(lambda i: i.user.guild_permissions.administrator)
    async def set_roles(
        self, 
        interaction: discord.Interaction, 
        user_role:discord.Role, 
        admin_role:discord.Role,
        announce_channel:discord.TextChannel
    ):
        database = self.bot.get_database(interaction.guild_id)
        server_manager = self.bot.get_server_manager(interaction.guild_id)
        server_manager.guild_setting.user_role_id = user_role.id
        server_manager.guild_setting.admin_role_id = admin_role.id
        server_manager.guild_setting.announce_channel_id = announce_channel.id
        
        result_embed = discord.Embed(
            title="다음과 같이 서버 설정이 정해졌습니다!",
            color=Colour.green()
        )
        result_embed.add_field(name="유저 역할", value=user_role.mention)
        result_embed.add_field(name="관리자 역할", value=admin_role.mention)
        result_embed.add_field(name="공지 채널", value=announce_channel.mention)
        
        await interaction.response.send_message(embed=result_embed)
        
        server_manager.guild_setting.push()
        database.connection.commit()

async def setup(bot: BotBase):
    await bot.add_cog(GuildManagement(bot))