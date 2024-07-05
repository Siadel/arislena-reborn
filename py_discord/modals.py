import discord
from discord.ui import Modal, TextInput

from py_base.koreanstring import objective, instrumental
from py_base.ari_enum import BuildingCategory, ResourceCategory
from py_system.systemobj import Crew, Livestock
from py_system.tableobj import Faction, FactionHierarchyNode, Territory, Building, Resource
from py_discord import func
from py_discord.bot_base import BotBase

class ArislenaTextInput(TextInput):
    
    def __init__(
        self,
        label:str,
        *,
        min_length:int = 1,
        max_length:int = 30,
        placeholder:str = "한글, 다이어크리틱 없는 영문, 숫자, 공백만 허용됩니다.",
        style:discord.TextStyle = discord.TextStyle.short
    ):
        super().__init__(
            label=label,
            min_length=min_length,
            max_length=max_length,
            placeholder=placeholder,
            style=style
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

    faction_name = ArislenaTextInput("세력 이름")
    
    def __init__(self, *, bot:BotBase = None):
        super().__init__(title="세력 창설")
        self.bot = bot

    async def on_submit(self, interaction:discord.Interaction):

        faction_name = self.faction_name.value.strip()
        # 특수문자가 포함되어 있는지 확인
        func.check_special_character_and_raise(faction_name)
        
        database = self.bot.get_database(interaction.guild_id)

        # 세력 데이터베이스에 추가
        new_faction = func.make_and_push_new_faction(database, Faction(user_id=interaction.user.id, name=faction_name))

        # id가 가장 낮은 세력의 하위 세력으로 설정
        optimal_faction = Faction.from_database(database, "id = (SELECT MIN(id) FROM faction)")
        new_fhn = FactionHierarchyNode()
        new_fhn.set_database(database)
        new_fhn.push(new_faction, optimal_faction)
        
        # 경험치가 12인 대원 2명 추가
        # TODO 리팩토링으로 인해 이 부분을 다시 작성해야 함
        for _ in range(2):
            func.make_and_push_new_crew_package(
                database, Crew.new(new_faction.id)
            )
        
        # 자원 추가: 식량 6, 식수 6
        Resource(faction_id=new_faction.id, category=ResourceCategory.FOOD, amount=6)\
            .set_database(database)\
            .push()
        Resource(faction_id=new_faction.id, category=ResourceCategory.WATER, amount=6)\
            .set_database(database)\
            .push()
            
        # 기본 영토와 건물(담수원, 수렵지, 목초지, 채집지) 추가
        func.add_new_territory_set(database, new_faction)
        
        database.connection.commit()

        await interaction.response.send_message(f"성공적으로 세력을 창설했습니다!", ephemeral=True)
        
        await self.bot.announce_channel(f"**{interaction.user.display_name}**님께서 **{self.faction_name}** 세력을 창설했어요!", self.bot.get_server_manager(interaction.guild_id).guild_setting.announce_channel_id)

class NewTerritoryModal(ArislenaGeneralModal):

    territory_name = ArislenaTextInput("영토 이름")

    def __init__(self, *, bot:BotBase = None):
        super().__init__(title="새 영토예요!")
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        
        territory_name = self.territory_name.value.strip()
        # 특수문자가 포함되어 있는지 확인
        func.check_special_character_and_raise(territory_name)
        
        database = self.bot.get_database(interaction.guild_id)

        # 세력 데이터베이스에 추가
        faction = Faction.from_database(database, user_id=interaction.user.id)
        # 새 영토 생성
        t = Territory(faction_id=faction.id, name=territory_name)
        t.set_safety_by_random()
        t.set_database(database)
        t.push()
        # 생성된 영토 데이터 가져오기
        t = Territory.from_database(database, "id = (SELECT MAX(id) FROM territory)")
        # 기본 건물 중 하나를 생성
        b_cat = BuildingCategory.get_ramdom_base_building_category()
        b = Building(
            faction_id=faction.id,
            territory_id=t.id,
            category=b_cat,
            name=b_cat.local_name
        )
        b.set_database(database)
        b.push()

        await interaction.response.send_message(f"성공적으로 **{territory_name}** 영토를 생성했습니다!", ephemeral=True)

        await self.bot.announce_channel(f"**{interaction.user.display_name}**님께서 새로운 영토, {objective(territory_name, '**')} 얻었어요!", self.bot.get_server_manager(interaction.guild_id).guild_setting.announce_channel_id)

        database.connection.commit()

class NewBuildingModal(ArislenaGeneralModal):
    
    building_name = ArislenaTextInput("건물 이름")
    
    def __init__(self, *, bot:BotBase = None):
        super().__init__(title="새 건물이예요!")
        self.bot = bot
        
    async def on_submit(self, interaction: discord.Interaction) -> None:
        raise NotImplementedError()

class NameCrewModal(ArislenaGeneralModal):
    
    new_crew_name = ArislenaTextInput("대원 이름")
    
    def __init__(self, bot:BotBase, previous_crew_name:str):
        super().__init__(title="대원 이름 정하기")
        self.bot = bot
        self.previous_crew_name = previous_crew_name
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.from_database(database, user_id=interaction.user.id)
        crew = Crew.from_database(database, faction_id=faction.id, name=self.previous_crew_name)
        before_crew_name = crew.name
        crew.name = self.new_crew_name.value
        crew.push()
        
        await interaction.response.send_message(f"대원 이름을 **{before_crew_name}**에서 {instrumental(self.new_crew_name.value, '**')} 변경했습니다.\n버튼 내용은 변경되지 않으므로, 확인을 위해서는 새로 정보를 열람하셔야 합니다.", ephemeral=True)
        
        database.connection.commit()

class TrainLivestockModal(ArislenaGeneralModal):
    
    new_livestock_name = ArislenaTextInput("가축 이름")
    
    def __init__(self, *, bot: BotBase):
        super().__init__(title="가축 이름 정하기")
        self.bot = bot
        
    async def on_submit(self, interaction: discord.Interaction) -> None:
        database = self.bot.get_database(interaction.guild_id)
        
        faction = Faction.from_database(database, user_id=interaction.user.id)
        livestock = Livestock(
            faction_id=faction.id,
            name=self.new_livestock_name.value
        )
        livestock.set_database(database)
        livestock.push()
        
        await interaction.response.send_message(f"가축 이름을 {instrumental(self.new_livestock_name.value, '**')} 정하고, 노동에 활용할 수 있도록 새로 훈련했습니다.", ephemeral=True)
        