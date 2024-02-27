import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_discord import warnings, views
from py_discord.bot_base import BotBase
from py_base.ari_enum import TerritorySafety
from py_system.global_ import main_db, game_setting
from py_system.tableobj import Faction, Territory, deserialize
from py_discord.modals import NewTerritoryModal

class TerritoryCommand(GroupCog, name="영토"):

    @app_commands.command(
        name = "열람", 
        description = "영토의 정보를 열람할 수 있는 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다."
    )
    async def lookup(self, interaction: discord.Interaction):
        
        # 모든 영토 정보 가져오기
        territory_data_list = main_db.fetch_all("territory")
        territory_list = [deserialize(Territory, data) for data in territory_data_list]
        
        # 세력 정보 열람 버튼 ui 출력
        await interaction.response.send_message(
            "영토 정보 열람", 
            view=views.LookupView(
                territory_list,
                button_class=views.TerritoryLookupButton,
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

        # TODO 기능 코드 작성
        
        await interaction.response.send_modal(
            NewTerritoryModal(bot=self.bot)
        )

    @app_commands.command(
        name = "정화",
        description = "🕒영토를 정화합니다. 악마들과 마주칠 것입니다! 승리하면 영토의 정화 단계를 1단계 올립니다."
    )
    @app_commands.describe(
        territory_name = "영토 이름 (영토 이름이나 아이디 중 하나는 필수로 입력해야 합니다.)",
        territory_id = "영토 아이디 (영토 이름이나 아이디 중 하나는 필수로 입력해야 합니다.)"
    )
    async def purify(self, interaction: discord.Interaction, territory_name:str=None, territory_id:int=None):
        
        if territory_name is None and territory_id is None: raise warnings.NoInput()

        if territory_name and territory_id: raise warnings.DuplicatedInput()

        territory: Territory = None

        if territory_name: territory = Territory.from_database(main_db, name=territory_name)
        elif territory_id: territory = Territory.from_database(main_db, id=territory_id)

        # TODO 기능 코드 작성

        if territory.safety == TerritorySafety.max_value():
            interaction.response.send_message("이미 최대 정화 단계입니다.", ephemeral=True)
            return
        territory.safety = TerritorySafety(territory.safety.value + 1)

async def setup(bot: BotBase):
    await bot.add_cog(TerritoryCommand(bot), guilds=bot.objectified_guilds)