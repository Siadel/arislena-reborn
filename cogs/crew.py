import discord
from discord.ext.commands import GroupCog
from discord import app_commands
from sqlite3 import Row
import random

from py_base.ari_enum import FacilityCategory, CommandCategory
from py_discord.bot_base import BotBase
from py_discord import views, warnings, func
from py_system.worker import Crew
from py_system.tableobj import Faction, CommandCounter, Worker

class CrewCommand(GroupCog, name="대원"):
    
    def __init__(self, bot: BotBase):
        super().__init__()
        self.bot = bot
    
    @app_commands.command(
        name = "모집",
        description = "새 대원을 세력으로 편입합니다."
    )
    @app_commands.describe(
        try_count = "모집 횟수; 기본값은 1입니다. 최대 모집 횟수는 `1 + (소유 중인 모병소 수)`입니다. 입력한 값이 최대 모집 횟수를 초과하면, 최대 모집 횟수로 설정됩니다."
    )
    async def recruit(self, interaction: discord.Interaction, try_count:int = 1):
        # 다음 턴이 시작할 때 일정 수(0~2)의 대원을 추가한다. 매 턴 1회 가능하다. 팩션이 소유 중인 모병소에 따라 턴 당 최대 횟수가 증가한다.
        
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=interaction.user.id).set_database(database)
        
        recruit_counter:CommandCounter = faction.get_command_counter(CommandCategory.RECRUIT)
        recruit_counter.set_database(database)
        territory_ids:list[Row] = database.connection.execute(f"SELECT id FROM territory WHERE faction_id = {faction.id}").fetchall()
        recruit_limit = 1
        for territory_id in territory_ids:
            recruit_limit += database.fetch_many(
                "facility", category=FacilityCategory.RECRUITING_CAMP.value, territory_id=territory_id["id"]
            ).__len__()
        
        if try_count + recruit_counter.amount > recruit_limit: try_count = recruit_limit - recruit_counter.amount
        else: recruit_counter.amount += try_count
        
        if try_count == 0: await interaction.response.send_message("남은 모집 횟수가 없습니다."); return
        
        members_recruited = 0
        for _ in range(try_count):
            # 0명: 20%, 1명: 70%, 2명: 10%
            members_recruited += random.choices([0, 1, 2], [0.2, 0.7, 0.1])[0]
        
        for _ in range(members_recruited):
            func.make_and_push_new_crew_package(database, Crew.new(faction.id), self.bot.get_server_manager(interaction.guild_id).detail)
        
        await interaction.response.send_message(f"모집 횟수를 {try_count}회 사용해 새 인원을 {members_recruited}명 모집했습니다.")
        
        recruit_counter.push()
        database.connection.commit()
    
    @app_commands.command(
        name = "열람",
        description = "세력이 가지고 있는 대원 목록을 열람합니다."
    )
    async def lookup(self, interaction: discord.Interaction):
        
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=interaction.user.id)
        
        crew_list = [Crew.from_data(data) for data in database.fetch_many(Crew.table_name, faction_id=faction.id)]
        
        await interaction.response.send_message(
            "대원 목록",
            view=views.TableObjectView(
                crew_list, 
                sample_button=views.CrewLookupButton(self.bot, interaction)
            )
        )
    
    @app_commands.command(
        name = "명명",
        description = "세력이 가지고 있는 대원의 이름을 정합니다."
    )
    async def name(self, interaction: discord.Interaction):
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=interaction.user.id)

        crew_list = [Crew.from_data(data) for data in database.fetch_many(Crew.table_name, faction_id=faction.id)]
        
        await interaction.response.send_message(
            "대원 목록",
            view=views.TableObjectView(
                crew_list, 
                sample_button=views.CrewNameButton(self.bot, interaction)
            )
        )
    
    @app_commands.command(
        name = "배치",
        description = "세력이 가지고 있는 대원을 시설에 배치합니다. 이미 배치되어 있는 경우에도 사용할 수 있습니다."
    )
    async def deploy(self, interaction: discord.Interaction):
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=interaction.user.id)
        
        crew_list = [Crew.from_data(data) for data in database.fetch_many(Crew.table_name, faction_id=faction.id)]
        
        await interaction.response.send_message(
            "대원 목록",
            view=views.TableObjectView(
                crew_list, 
                sample_button=views.SelectCrewToDeployButton(self.bot, interaction, faction)
            )
        )
        
    @app_commands.command(
        name = "해고",
        description = "[관리자 전용] 세력이 가지고 있는 대원을 없앱니다."
    )
    async def dismiss(self, interaction: discord.Interaction):
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.fetch_or_raise(database, warnings.NoFaction(), user_id=interaction.user.id)
        
        crew_list = [Crew.from_data(data) for data in database.fetch_many(Crew.table_name, faction_id=faction.id)]
        
        await interaction.response.send_message(
            "대원 목록",
            view=views.TableObjectView(
                crew_list, 
                sample_button=views.CrewDismissButton(self.bot, interaction)
            )
        )

async def setup(bot: BotBase):
    await bot.add_cog(CrewCommand(bot))