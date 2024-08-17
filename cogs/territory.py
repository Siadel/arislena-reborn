import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_base.ari_enum import TerritorySafety
from py_system.tableobj import Territory, Faction
from py_discord import views
from py_discord.bot_base import BotBase
from py_discord.modals import NewTerritoryModal
from py_base import warnings

class TerritoryCommand(GroupCog, name="영토"):
    
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name = "열람", 
        description = "자신 소유 영토의 정보를 열람할 수 있는 버튼 ui를 출력합니다. 버튼 ui는 180초 후 비활성화됩니다."
    )
    async def lookup(self, interaction: discord.Interaction):
        
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=interaction.user.id)
        # 모든 영토 정보 가져오기
        territory_data_list = database.fetch_many(Territory.table_name, faction_id=faction.id)
        territory_list = [Territory.from_data(data) for data in territory_data_list]
        
        # 세력 정보 열람 버튼 ui 출력
        await interaction.response.send_message(
            "영토 정보 열람", 
            view=views.TableObjectView(
                territory_list,
                sample_button=views.TerritoryLookupButton(self.bot, interaction, faction)
            )
        )

    @app_commands.command(
        name = "정찰",
        description = "🕒미지의 영토를 정찰합니다. 악마들과 마주칠 것입니다! 승리하면 영토를 획득합니다."
    )
    async def scout(self, interaction: discord.Interaction):

        Faction.fetch_or_raise(self.bot.get_database(interaction.guild_id), warnings.NoFaction(), user_id=interaction.user.id)

        # TODO 기능 코드 작성
        
        await interaction.response.send_modal(
            NewTerritoryModal(bot=self.bot)
        )

    @app_commands.command(
        name = "정화",
        description = "🕒영토를 정화합니다. 악마들과 마주칠 것입니다! 승리하면 영토의 정화 단계를 1단계 올립니다."
    )
    async def purify(self, interaction: discord.Interaction):
        
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=interaction.user.id)
        
        territory_list = database.fetch_many(Territory.table_name, faction_id=faction.id)

        await interaction.response.send_message(
            "정화할 영토를 선택해주세요.",
            view=views.TableObjectView(
                [Territory.from_data(data) for data in territory_list],
                sample_button=views.PurifyButton(self.bot, interaction, faction)
            )
        )
    

async def setup(bot: BotBase):
    await bot.add_cog(TerritoryCommand(bot))