import discord
from discord.ui import Modal, TextInput

from py_base.koreanstring import objective, instrumental
from py_base.ari_enum import BuildingCategory, ResourceCategory
from py_system.tableobj import Faction, FactionHierarchyNode, Territory, Building, Crew, Resource
from py_system._global import self.bot.guild_database[str(interaction.guild_id)], name_regex, game_setting, translate
from py_discord import warnings, func
from py_discord.bot_base import AriBot

def get_basic_text_input(label:str):
    return TextInput(
        label=label,
        min_length=1,
        max_length=game_setting.name_length_limit,
        placeholder="한글, 다이어크리틱 없는 영문, 숫자, 공백만 허용됩니다.",
        style=discord.TextStyle.short
    )

# 테스트 모달
class ModalTest(Modal):

    name = TextInput(label='Name', max_length=50)
    answer = TextInput(label='Answer', style=discord.TextStyle.paragraph)

    def __init__(self):
        super().__init__(
            title='Test Modal',
            timeout=60.0
        )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Thanks for your response, {self.name}!', ephemeral=True)

class ArislenaGeneralModal(Modal):

    def __init__(self, title:str, timeout:float = 180.0):
        super().__init__(
            title = title,
            timeout = timeout
        )

    async def on_timeout(self, interaction:discord.Interaction):
        await interaction.response.send_message("시간이 초과되었습니다.", ephemeral=True)

class FactionCreateModal(ArislenaGeneralModal):

    faction_name = get_basic_text_input("세력 이름")
    
    def __init__(self, *, bot:AriBot = None):
        super().__init__(title="세력 창설")
        self.bot = bot

    async def on_submit(self, interaction:discord.Interaction):

        faction_name = self.faction_name.value.strip()
        # 특수문자가 포함되어 있는지 확인
        func.check_special_character_and_raise(faction_name)

        # 세력 데이터베이스에 추가
        new_faction = Faction(user_id=interaction.user.id, name=faction_name)
        new_faction.set_database(self.bot.guild_database[str(interaction.guild_id)])
        new_faction.push()

        # id가 가장 낮은 세력의 하위 세력으로 설정
        optimal_faction = Faction.from_database(self.bot.guild_database[str(interaction.guild_id)], "id = (SELECT MIN(id) FROM faction)")
        new_fhn = FactionHierarchyNode()
        new_fhn.set_database(self.bot.guild_database[str(interaction.guild_id)])
        new_fhn.push(new_faction, optimal_faction)
        
        # 경험치가 36인 대원 2명 추가
        for _ in range(2):
            new_crew = Crew.new(new_faction.id)\
                .set_database(self.bot.guild_database[str(interaction.guild_id)])
            new_crew.experience = 36
            new_crew.push()
        
        # 자원 추가: 식량 6, 식수 6
        Resource(faction_id=new_faction.id, category=ResourceCategory.FOOD, amount=6).push()
        Resource(faction_id=new_faction.id, category=ResourceCategory.WATER, amount=6).push()
        
        self.bot.guild_database[str(interaction.guild_id)].connection.commit()

        await interaction.response.send_message(f"성공적으로 세력을 창설했습니다!", ephemeral=True)
        
        await self.bot.announce(f"**{interaction.user.display_name}**님께서 **{self.faction_name}** 세력을 창설했어요!", interaction.guild.id)

class NewTerritoryModal(ArislenaGeneralModal):

    territory_name = get_basic_text_input("영토 이름")

    def __init__(self, *, bot:AriBot = None):
        super().__init__(title="새 영토예요!")
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        
        territory_name = self.territory_name.value.strip()
        # 특수문자가 포함되어 있는지 확인
        func.check_special_character_and_raise(territory_name)

        # 세력 데이터베이스에 추가
        faction = Faction.from_database(self.bot.guild_database[str(interaction.guild_id)], user_id=interaction.user.id)
        # 새 영토 생성
        t = Territory(faction_id=faction.id, name=territory_name)
        t.explicit_post_init()
        t.set_database(self.bot.guild_database[str(interaction.guild_id)])
        t.push()
        # 생성된 영토 데이터 가져오기
        t = Territory.from_database(self.bot.guild_database[str(interaction.guild_id)], "id = (SELECT MAX(id) FROM territory)")
        # 기본 건물 중 하나를 생성
        b_cat = BuildingCategory.get_ramdom_base_building_category()
        b = Building(
            faction_id=faction.id,
            territory_id=t.id,
            category=b_cat,
            name=b_cat.local_name
        )
        b.set_database(self.bot.guild_database[str(interaction.guild_id)])
        b.push()

        await interaction.response.send_message(f"성공적으로 **{territory_name}** 영토를 생성했습니다!", ephemeral=True)

        await self.bot.announce(f"**{interaction.user.display_name}**님께서 새로운 영토, {objective(territory_name, '**')} 얻었어요!", interaction.guild.id)

        self.bot.guild_database[str(interaction.guild_id)].connection.commit()

class NewBuildingModal(ArislenaGeneralModal):
    
    building_name = get_basic_text_input("건물 이름")
    
    def __init__(self, *, bot:AriBot = None):
        super().__init__(title="새 건물이예요!")
        self.bot = bot
        
    async def on_submit(self, interaction: discord.Interaction) -> None:
        raise NotImplementedError()

class NameCrew(ArislenaGeneralModal):
    
    new_crew_name = get_basic_text_input("대원 이름")
    
    def __init__(self, *, bot:AriBot = None, previous_crew_name:str = None):
        super().__init__(title="대원 이름 정하기")
        self.bot = bot
        self.previous_crew_name = previous_crew_name
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        
        faction = Faction.from_database(self.bot.guild_database[str(interaction.guild_id)], user_id=interaction.user.id)
        crew = Crew.from_database(self.bot.guild_database[str(interaction.guild_id)], faction_id=faction.id, name=self.previous_crew_name)
        crew.name = self.new_crew_name.value
        crew.push()
        
        await interaction.response.send_message(f"대원 이름을 {instrumental(self.new_crew_name.value, '**')} 변경했습니다.", ephemeral=True)
        
        self.bot.guild_database[str(interaction.guild_id)].connection.commit()