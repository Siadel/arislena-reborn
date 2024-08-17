import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_base.koreanstring import objective
from py_system.tableobj import Facility
from py_system.tableobj import Faction, Territory
from py_discord import views
from py_discord.bot_base import BotBase
from py_discord.func import get_facility_category_choices
from py_base import warnings

class FacilityCommand(GroupCog, name="시설"):
    
    def __init__(self, bot: BotBase):
        super().__init__()
        self.bot = bot
        
    @app_commands.command(
        name = "건설",
        description = "🕒자신이 소유한 영토에 시설을 건설합니다. 시설은 1개만 건설할 수 있습니다."
    )
    @app_commands.choices(
        facility_category = get_facility_category_choices()
    )
    @app_commands.describe(
        facility_category = "시설 종류",
        facility_name = "시설 이름"
    )
    async def build(self, interaction: discord.Interaction, facility_category: app_commands.Choice[int], facility_name: str):\
        
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=interaction.user.id)
        
        territory_list = database.fetch_many("territory", faction_id=faction.id)
        
        if len(territory_list) == 0:
            await interaction.response.send_message("건설할 영토가 없습니다.", ephemeral=True)
            
        facility_name_list = database.cursor.execute("SELECT name FROM facility").fetchall()
        if facility_name in facility_name_list: raise warnings.AlreadyExist("그 이름의 시설")
        
        await interaction.response.send_message(
            f"{objective(facility_category.name)} 선택하셨습니다. 건설할 영토를 선택해주세요.", 
            view=views.TableObjectView(
                [Territory.from_data(data) for data in territory_list],
                sample_button = views.BuildButton(
                    self.bot,
                    interaction,
                    faction,
                    facility_category=facility_category,
                    facility_name=facility_name
                )
            ),
            ephemeral=True
        )
    
    @app_commands.command(
        name = "열람",
        description = "자신 소유 영토의 시설을 열람합니다. 혹은 다른 유저 영토의 시설을 열람합니다."
    )
    @app_commands.describe(
        other_user = "다른 유저"
    )
    async def view(self, interaction: discord.Interaction, other_user: discord.User = None):
        
        database = self.bot.get_database(interaction.guild_id)
        
        user_id = other_user.id if other_user else interaction.user.id
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=user_id)
        
        b_list = database.fetch_many(Facility.table_name, faction_id = faction.id)
        
        await interaction.response.send_message(
            "열람할 시설을 선택해주세요.",
            view=views.TableObjectView(
                [Facility.from_data(data) for data in b_list],
                sample_button = views.FacilityLookupButton(self.bot, interaction)
            )
        )

async def setup(bot: BotBase):
    await bot.add_cog(FacilityCommand(bot))