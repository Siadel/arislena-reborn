import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_base.koreanstring import objective
from py_discord.bot_base import BotBase
from py_discord import check, warning
from py_system import tableobj, jsonobj
from py_system.database import main_db

class FactionCommand(GroupCog):

    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()
    
    @app_commands.command(
        name = "창설",
        description = "세력을 창설합니다."
    )
    @app_commands.describe(
        name = "세력명 (16자 이하)"
    )
    async def create(self, interaction: discord.Interaction, name:str):
        
        settings = jsonobj.Settings()

        # 이미 세력을 가지고 있는지 확인
        if main_db.fetch("faction", f"owner_id = {interaction.user.id}"):
            raise warning.AlreadyExist("창설한 세력")
        
        # 세력 이름이 16자 이하인지 확인
        limit = settings.content["faction_name_length_limit"]
        if len(name) > limit: raise warning.NameTooLong("세력명", limit)

        initial_faction_value = settings.content["initial_faction_value"]
        main_db.insert(tableobj.Faction(user_ID=interaction.user.id, name=name, **initial_faction_value))
        faction:tableobj.Faction = main_db.fetch("faction", f"owner_id = {interaction.user.id}")
        main_db.insert(tableobj.Knowledge(faction_ID=faction.ID))
        main_db.insert(tableobj.Faction_data(faction_ID=faction.ID))

        await interaction.response.send_message(f"성공적으로 세력을 창설했습니다! `/세력 수정` 명령어로 세력의 추가 정보를 넣거나 수정할 수 있습니다.", ephemeral=True)
        await self.bot.announce(f"{interaction.user.name}께서 {name} 세력을 창설했어요!")
    
    
    @app_commands.command(
        name = "수정",
        description = "창설한 세력의 정보를 수정합니다."
    )
    @app_commands.check(check.is_owner)
    async def edit(self, interaction: discord.Interaction, attribute:str, value:str = None, message_link:str = None):
        pass
    
    @app_commands.command(
        name = "강제수정",
        description = "관리자가 창설된 세력의 정보를 수정합니다."
    )
    @app_commands.check(check.is_admin)
    async def edit(self, interaction: discord.Interaction, faction_name:str):
        pass
    


async def setup(bot: BotBase):
    await bot.add_cog(FactionCommand(bot), guilds=bot.objectified_guilds)