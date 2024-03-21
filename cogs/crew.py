import discord
from discord.ext.commands import GroupCog
from discord import app_commands
from sqlite3 import Row
import random

from py_base.ari_enum import BuildingCategory, CommandCountCategory
from py_discord.bot_base import BotBase
from py_discord import checks, views, warnings, modals
from py_system.tableobj import Faction, CommandCounter, Crew
from py_system._global import main_db

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
        
        if (faction := Faction.from_database(main_db, user_id=interaction.user.id)) is None:
            raise warnings.NoFaction()
        
        recruit_counter:CommandCounter = faction.get_command_counter(CommandCountCategory.RECRUIT)
        recruit_counter.set_database(main_db)
        territory_ids:list[Row] = main_db.connection.execute(f"SELECT id FROM territory WHERE faction_id = {faction.id}").fetchall()
        recruit_limit = 1
        for territory_id in territory_ids:
            recruit_limit += main_db.fetch_many(
                "building", category=BuildingCategory.RECRUITING_CAMP.value, territory_id=territory_id["id"]
            ).__len__()
        
        if try_count + recruit_counter.amount > recruit_limit: try_count = recruit_limit - recruit_counter.amount
        else: recruit_counter.amount += try_count
        
        if try_count == 0: await interaction.response.send_message("남은 모집 횟수가 없습니다."); return
        
        members_recruited = 0
        for _ in range(try_count):
            members_recruited += random.randint(0, 2)
        
        for _ in range(members_recruited):
            random_number = str(random.random()).split(".")[1]
            new_crew = Crew(faction_id=faction.id, name=f"대원 {random_number}")
            new_crew.set_database(main_db)
            new_crew.push()
        
        await interaction.response.send_message(f"모집 횟수를 {try_count}회 사용해 새 인원을 {members_recruited}명 모집했습니다.")
        
        recruit_counter.push()
        main_db.connection.commit()
    
    @app_commands.command(
        name = "열람",
        description = "세력이 가지고 있는 대원 목록을 열람합니다."
    )
    async def lookup(self, interaction: discord.Interaction):
        
        if (faction := Faction.from_database(main_db, user_id=interaction.user.id)) is None:
            raise warnings.NoFaction()
        
        crew_list = [Crew.from_data(data) for data in main_db.fetch_many("crew", faction_id=faction.id)]
        
        await interaction.response.send_message(
            "대원 목록",
            view=views.TableObjectView(
                crew_list, 
                button_class=views.CrewLookupButton,
                bot=self.bot
            )
        )
    
    @app_commands.command(
        name = "명명",
        description = "세력이 가지고 있는 대원의 이름을 정합니다."
    )
    async def name(self, interaction: discord.Interaction):
        
        if (faction := Faction.from_database(main_db, user_id=interaction.user.id)) is None:
            raise warnings.NoFaction()

        crew_list = [Crew.from_data(data) for data in main_db.fetch_many("crew", faction_id=faction.id)]
        
        await interaction.response.send_message(
            "대원 목록",
            view=views.TableObjectView(
                crew_list, 
                button_class=views.CrewNameButton,
                bot=self.bot
            )
        )

async def setup(bot: BotBase):
    await bot.add_cog(CrewCommand(bot), guilds=bot.objectified_guilds)