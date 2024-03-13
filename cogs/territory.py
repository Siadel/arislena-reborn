import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_base.ari_enum import TerritorySafety
from py_system._global import main_db
from py_system.tableobj import Territory
from py_discord import warnings, views
from py_discord.bot_base import BotBase
from py_discord.modals import NewTerritoryModal

class TerritoryCommand(GroupCog, name="영토"):
    
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name = "열람", 
        description = "영토의 정보를 열람할 수 있는 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다."
    )
    async def lookup(self, interaction: discord.Interaction):
        
        # 모든 영토 정보 가져오기
        territory_data_list = main_db.fetch_all("territory")
        territory_list = [Territory.from_data(data) for data in territory_data_list]
        
        # 세력 정보 열람 버튼 ui 출력
        await interaction.response.send_message(
            "영토 정보 열람", 
            view=views.TableObjectView(
                territory_list,
                button_class=views.TerritoryLookupButton,
                bot=self.bot
            )
        )

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
    async def purify(self, interaction: discord.Interaction):
        
        if not main_db.is_exist("faction", f"user_id = {interaction.user.id}"): raise warnings.NoFaction()
        
        territory_list = main_db.fetch_many("territory", f"faction_id = (SELECT id FROM faction WHERE user_id = {interaction.user.id})")
        
        if len(territory_list) == 0:
            await interaction.response.send_message("정화할 영토가 없습니다.", ephemeral=True)

        await interaction.response.send_message(
            "정화할 영토를 선택해주세요.",
            view=views.TableObjectView(
                [Territory.from_data(data) for data in territory_list],
                button_class=views.PurifyButton,
                bot=self.bot,
                prev_interaction=interaction
            )
        )
    

async def setup(bot: BotBase):
    await bot.add_cog(TerritoryCommand(bot), guilds=bot.objectified_guilds)