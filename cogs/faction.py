import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord.bot_base import BotBase
from py_discord import views, warnings, modals
from py_system.tableobj import Faction

class FactionCommand(GroupCog, name="세력"):

    def __init__(self, bot: BotBase):
        super().__init__()
        self.bot = bot
    
    @app_commands.command(
        name = "창설",
        description = "세력을 창설합니다. 관리자가 아닌 경우, 세력 1개만 창설할 수 있습니다."
    )
    async def create(self, interaction: discord.Interaction):

        if not self.bot.get_database(interaction.guild_id).is_exist("user", f"discord_id = {interaction.user.id}"):
            raise warnings.NotRegistered(interaction.user.display_name)

        # 이미 세력을 가지고 있는지 확인 (관리자는 예외)
        if self.bot.get_database(interaction.guild_id).is_exist("faction", f"user_id = {interaction.user.id}") and not self.bot.check_admin(interaction.user):
            raise warnings.AlreadyExist("창설한 세력")
        
        await interaction.response.send_modal(modals.FactionCreateModal(bot=self.bot))
    
    @app_commands.command(
        name = "열람", 
        description = "세력의 정보를 열람할 수 있는 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다."
    )
    async def lookup(self, interaction: discord.Interaction):
        
        # 모든 세력 정보 가져오기
        faction_data_list = self.bot.get_database(interaction.guild_id).fetch_all("faction")
        faction_list = [Faction.from_data(data) for data in faction_data_list]
        
        # 세력 정보 열람 버튼 ui 출력
        await interaction.response.send_message(
            "세력 정보 열람", 
            view=views.TableObjectView(
                faction_list,
                sample_button=views.FactionLookupButton(interaction)\
                    .set_database(self.bot.get_database(interaction.guild_id))
            )
        )
    
    @app_commands.command(
        name = "수정",
        description = "창설한 세력의 정보를 수정합니다. 다른 세력의 정보를 수정하려면 관리자 권한이 필요합니다."
    )
    async def edit(self, interaction: discord.Interaction, attribute:str, value:str = None, message_link:str = None, faction_id:int = None):
        pass

    @app_commands.command(
        name = "해산",
        description = "[관리자 전용] 세력을 해산하여 데이터에서 삭제합니다."
    )
    async def delete(self, interaction: discord.Interaction):
        self.bot.check_admin_or_raise(interaction)
        # 모든 세력 정보 가져오기
        faction_data_list = self.bot.get_database(interaction.guild_id).fetch_all("faction")
        faction_list = [Faction.from_data(data) for data in faction_data_list]
        for faction in faction_list: faction.set_database(self.bot.get_database(interaction.guild_id))
        
        await interaction.response.send_message(
            "세력 해산", 
            view=views.TableObjectView(
                faction_list,
                sample_button=views.FactionDeleteButton(interaction)\
                    .set_database(self.bot.get_database(interaction.guild_id))\
                    .set_bot(self.bot)
            ),
            ephemeral=True
        )
    
    @app_commands.command(
        name = "위계설정",
        description = "[관리자 전용] 세력의 위계를 설정합니다."
    )
    async def set_hierarchy(self, interaction: discord.Interaction):
        pass

    

async def setup(bot: BotBase):
    await bot.add_cog(FactionCommand(bot))