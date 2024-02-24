import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord import warnings, views
from py_discord.bot_base import BotBase
from py_system.global_ import main_db, game_setting
from py_system.tableobj import Faction, Territory
from py_discord.modals import NewTerritoryModal

class TerritoryCommand(GroupCog, name="영토"):

    @app_commands.command(
        name = "열람", 
        description = "세력의 정보를 열람할 수 있는 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다."
    )
    async def lookup(self, interaction: discord.Interaction):
        
        # 모든 영토 정보 가져오기
        territory_data_list = main_db.fetch_all("territory")
        territory_list = [Territory(**data) for data in territory_data_list]
        for territory in territory_list: territory.database = main_db
        
        # 세력 정보 열람 버튼 ui 출력
        await interaction.response.send_message(
            "영토 정보 열람", 
            view=views.LookupView(
                territory_list,
                button_class=views.FactionLookupButton,
                bot=self.bot,
                interaction=interaction)
        )

    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name = "정찰",
        description = "🕒미지의 영토를 정찰합니다. 악마들과 마주칠 것입니다! 승리하면 영토를 획득합니다."
    )
    async def scout(self, interaction: discord.Interaction):

        if not main_db.is_exist("faction", f"user_id = {interaction.user.id}"): raise warnings.NoFaction()
        
        await interaction.response.send_modal(
            NewTerritoryModal(bot=self.bot)
        )

async def setup(bot: BotBase):
    await bot.add_cog(TerritoryCommand(bot), guilds=bot.objectified_guilds)