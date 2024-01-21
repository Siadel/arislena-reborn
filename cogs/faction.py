import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_base import koreanstring
from py_discord.bot_base import BotBase
from py_discord import check, warning, view
from py_system import tableobj, jsonobj
from py_system.ari_global import main_db, name_ban

class FactionCommand(GroupCog, name="세력"):

    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()
    
    @app_commands.command(
        name = "창설",
        description = "세력을 창설합니다."
    )
    @app_commands.describe(
        faction_name = "세력명 (50바이트 이하)"
    )
    async def create(self, interaction: discord.Interaction, faction_name:str):
        
        settings = jsonobj.Settings()

        # 이미 세력을 가지고 있는지 확인
        if main_db.fetch("faction", f"user_id = {interaction.user.id}"):
            raise warning.AlreadyExist("창설한 세력")
        
        # 특수문자가 포함되어 있는지 확인
        if name_ban.search(faction_name): raise warning.NameContainsSpecialCharacter()
        
        # 세력 이름이 바이트 조건에 만족하는지 확인
        limit = settings.content["faction_name_byte_limit"]
        if faction_name.encode("utf-8").__len__() > limit: raise warning.NameTooLong("세력명", limit)

        main_db.insert(tableobj.Faction(user_ID=interaction.user.id, name=faction_name))

        await interaction.response.send_message(f"성공적으로 세력을 창설했습니다!", ephemeral=True)
        await self.bot.announce(f"**{interaction.user.display_name}**님께서 **{faction_name}** 세력을 창설했어요!", interaction.guild.id)
    
    @app_commands.command(
        name = "열람", 
        description = "세력의 정보를 열람할 수 있는 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다."
    )
    async def lookup(self, interaction: discord.Interaction):
        
        # 모든 세력 정보 가져오기
        faction_list = main_db.fetch_all("faction")
        
        # 세력 정보 열람 버튼 ui 출력
        await interaction.response.send_message(
            "세력 정보 열람", 
            view=view.GeneralLookupView(
                faction_list, 
                display_column="name")
        )
    
    @app_commands.command(
        name = "수정",
        description = "창설한 세력의 정보를 수정합니다. 다른 세력의 정보를 수정하려면 관리자 권한이 필요합니다."
    )
    @app_commands.check(check.is_owner)
    async def edit(self, interaction: discord.Interaction, attribute:str, value:str = None, message_link:str = None, faction_id:int = None):
        pass

    @app_commands.command(
        name = "해산",
        description = "[관리자 전용] 세력을 해산하여 데이터에서 삭제합니다."
    )
    @app_commands.check(check.is_admin)
    async def delete(self, interaction: discord.Interaction):
        
        await interaction.response.send_message(
            "세력 해산", 
            view=view.GeneralLookupView(
                main_db.fetch_all("faction"), 
                display_column="name", 
                button_class=view.FactionDeleteButton
            )
        )


async def setup(bot: BotBase):
    await bot.add_cog(FactionCommand(bot), guilds=bot.objectified_guilds)