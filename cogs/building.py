import discord
from discord.ext.commands import GroupCog
from discord import app_commands

from py_base.koreanstring import objective
from py_system._global import main_db
from py_system.tableobj import Faction, Territory, Building
from py_discord import warnings, views
from py_discord.bot_base import BotBase
from py_discord.func import get_building_category_choices

class BuildingCommand(GroupCog, name="건물"):
    
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()
        
    @app_commands.command(
        name = "건설",
        description = "🕒자신이 소유한 영토에 건물을 건설합니다. 건물은 1개만 건설할 수 있습니다."
    )
    @app_commands.choices(
        building_category = get_building_category_choices()
    )
    @app_commands.describe(
        building_category = "건물 종류",
        building_name = "건물 이름"
    )
    async def build(self, interaction: discord.Interaction, building_category: app_commands.Choice[int], building_name: str):

        if not main_db.is_exist("faction", f"user_id = {interaction.user.id}"): raise warnings.NoFaction()
        
        territory_list = main_db.fetch_many("territory", f"faction_id = (SELECT id FROM faction WHERE user_id = {interaction.user.id})")
        
        if len(territory_list) == 0:
            await interaction.response.send_message("건설할 영토가 없습니다.", ephemeral=True)
            
        building_name_list = main_db.cursor.execute("SELECT name FROM building").fetchall()
        if building_name in building_name_list: raise warnings.AlreadyExist("그 이름의 건물")
        
        await interaction.response.send_message(
            f"{objective(building_category.name)} 선택하셨습니다. 건설할 영토를 선택해주세요.", 
            view=views.TableObjectView(
                [Territory.from_data(data) for data in territory_list],
                sample_button = views.BuildButton(
                    building_category=building_category,
                    building_name=building_name
                )\
                    .set_previous_interaction(interaction)
            )
        )
    
    @app_commands.command(
        name = "열람",
        description = "자신 소유 영토의 건물을 열람합니다. 혹은 다른 유저 영토의 건물을 열람합니다."
    )
    @app_commands.describe(
        other_user = "다른 유저"
    )
    async def view(self, interaction: discord.Interaction, other_user: discord.User = None):
        
        f_data = None
        
        if not other_user and not (f_data := main_db.fetch(Faction.__name__, user_id = interaction.user.id)): raise warnings.NoFaction()
        elif other_user and not (f_data := main_db.fetch(Faction.__name__, user_id = other_user.id)): raise warnings.NoFaction()
        
        f = Faction.from_data(f_data)
        
        b_list = main_db.fetch_many(Building.__name__, faction_id = f.id)
        
        await interaction.response.send_message(
            "열람할 건물을 선택해주세요.",
            view=views.TableObjectView(
                [Building.from_data(data) for data in b_list],
                sample_button = views.BuildingLookupButton()
            )
        )

async def setup(bot: BotBase):
    await bot.add_cog(BuildingCommand(bot), guilds=bot.objectified_guilds)