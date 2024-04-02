import discord
from discord.ui import View, Button
from discord import ui, Colour

from py_base.koreanstring import nominative
from py_base.ari_enum import BuildingCategory, TerritorySafety
from py_system._global import main_db
from py_system.tableobj import TableObject, User, Faction, Territory, Building, Crew, Deployment
from py_discord import warnings, modals
from py_discord.embeds import table_info
from py_discord.bot_base import BotBase

# /유저 설정 - 설정 정보 출력
# 설정의 한국어명과 설정값 출력
# 설정값을 바꾸는 것으로 실제 설정을 바꿀 수 있어야 함

# class user_setting_view(View):

#     def __init__(self, user_setting:User_setting, *, timeout = 180):
#         super().__init__(timeout = timeout)
#         self.user_setting = user_setting

#         for key, value in user_setting.kr_dict_without_id.items():
#             self.add_item(user_setting_button(key, value))
    
#     @Button(label = "닫기", style = discord.ButtonStyle.danger)
#     async def close(self, interaction:discord.Interaction, button:discord.Button):
#         await interaction.response.edit_message(content = "설정 닫힘", view = None)

# class user_setting_button(Button):

#     def __init__(self, key:str, value:str):
#         super().__init__(label = key, style = discord.ButtonStyle.secondary)
#         self.key = key
#         self.value = value
    
#     async def callback(self, interaction:discord.Interaction):
#         await interaction.response.send_message(f"{self.key} : **{self.value}**", ephemeral = True)

# 범용 데이터 없음 표시 버튼
class NoDataButton(Button):

    def __init__(self, *, style = discord.ButtonStyle.danger):
        super().__init__(label = "데이터 없음", style = style, disabled = True)
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message("데이터 없음", ephemeral = True)

# 범용 열람 버튼
# 인자로 table 이름을 받아서 해당 테이블의 name column과 ID column을 출력
# 출력 양식은 "이름 (ID : %d)" 형태
        
class TableObjectButton(Button):
    
    def __init__(self):
        """
        사용법:
        ```python3
        btn = TableObjectButton(...).set_table_object(table_object)
        ```
        """        
        super().__init__(style = discord.ButtonStyle.primary)
        
        self._table_object:TableObject = None
        self.label_complementary:str = None
        
    def check_type(self, object, intended_type:TableObject):
        if type(object) != intended_type:
            raise TypeError(f"{object.__class__.__name__} 클래스는 {intended_type.__name__} 클래스의 객체와만 호환됩니다.")
        
    def set_label_complementary(self, table_object:TableObject):
        raise NotImplementedError()
        
    def set_table_object(self, table_object:TableObject):
        self.check_type(table_object)
        self.set_label_complementary(table_object)
        
        self._table_object = table_object
        return self
    
    def build(self):
        label_txt = self._table_object.display()

        if self.label_complementary: label_txt += f" ({self.label_complementary})"
        # <메인으로 출력할 데이터> (<서브로 보여줄 데이터 컬럼 한국어명> : <서브로 출력할 데이터>) 형태
        self.label = label_txt
        return self
    
    def _get_basic_embed(self):
        return table_info(
            discord.Embed(title = f"{self.label} 정보", color = Colour.green()), 
            self._table_object
        )
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(
            embed = self._get_basic_embed(),
            ephemeral = False # 일단은 False로
        )
        
class UserLookupButton(TableObjectButton):

    def __init__(self, prev_interaction:discord.Interaction):
        super().__init__()
        self.prev_interaction = prev_interaction
        self.user: User = None
        
    def check_type(self, user: User):
        super().check_type(user, User)
        
    def set_label_complementary(self, user: User):
        member = discord.utils.get(self.prev_interaction.guild.members, id = user.discord_id)
        self.label_complementary = f"{member.display_name}"
    
    def set_table_object(self, user: User):
        self.user = user
        return super().set_table_object(user)

class FactionLookupButton(TableObjectButton):

    def __init__(self, prev_interaction:discord.Interaction):
        super().__init__()
        self.prev_interaction = prev_interaction
        self.faction: Faction = None
        
    def check_type(self, faction: Faction):
        super().check_type(faction, Faction)
    
    def set_label_complementary(self, faction: Faction):
        user = discord.utils.get(self.prev_interaction.guild.members, id = faction.user_id)
        self.label_complementary = f"소유자 : {user.display_name}"
        
    def set_table_object(self, faction: Faction):
        self.faction = faction
        return super().set_table_object(faction)

class TerritoryLookupButton(TableObjectButton):

    def __init__(self):
        super().__init__()
        self.territory: Territory = None
        
    def check_type(self, territory: Territory):
        super().check_type(territory, Territory)
    
    def set_label_complementary(self, territory: Territory):
        self.faction = Faction.from_database(main_db, id = territory.faction_id)
        self.label_complementary = f"소유 세력 : {self.faction.name}"
    
    def set_table_object(self, territory: Territory):
        self.territory = territory
        return super().set_table_object(territory)
    
    async def callback(self, interaction:discord.Interaction):
        embed = self._get_basic_embed()
        # 건물 정보 추가
        buildings = main_db.fetch_many("building", territory_id = self.territory.id)
        field_value = ""
        
        if buildings:
            for building in buildings:
                building_object = Building.from_data(building)
                field_value += f"- {building_object.name} ({building_object.category.emoji} {building_object.category.local_name})\n"
        else:
            field_value = "- 건물 없음"
        
        embed.add_field(
            name="건물 정보",
            value=field_value
        )
        
        await interaction.response.send_message(
            embed = embed,
            ephemeral = False # 일단은 False로
        )

class CrewLookupButton(TableObjectButton):
    
    def __init__(self):
        super().__init__()
        self.crew: Crew = None
        
    def check_type(self, crew: Crew):
        super().check_type(crew, Crew)
        
    def set_label_complementary(self, crew: Crew):
        self.label_complementary = f"아이디 : {crew.id}"
        
    def set_table_object(self, crew: Crew):
        self.crew = crew
        return super().set_table_object(crew)

class CrewNameButton(CrewLookupButton):
    
    def __init__(self, bot: BotBase):
        super().__init__()
        self.bot = bot
    
    async def callback(self, interaction:discord.Interaction):
        
        await interaction.response.send_modal(modals.NameCrew(bot = self.bot, previous_crew_name = self.crew.name))

class CrewDeployButton(CrewLookupButton):
    
    def __init__(self, prev_interaction:discord.Interaction, prev_deploy: Deployment):
        super().__init__()
        self.prev_interaction = prev_interaction
        self.prev_deploy = prev_deploy
    
    def set_table_object(self, crew: Crew):
        self.label_complementary = "" # 예상 가능한 버그 발견함. 구조를 고쳐야 하는데 ...
        return super().set_table_object(crew)
    
    async def callback(self, interaction:discord.Interaction):
        
        # deployment 가져오기
        d = main_db.fetch(Deployment.__name__, crew_id = self.crew.id)

class PurifyButton(TerritoryLookupButton):
    
    def __init__(self, prev_interaction:discord.Interaction):
        super().__init__()
        self.prev_interaction = prev_interaction
    
    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.id != self.prev_interaction.user.id: raise warnings.ImpossibleToInterrupt()
        
        self.territory.set_database(main_db)
        
        if self.territory.safety.value == TerritorySafety.max_value():
            await interaction.response.send_message("이미 최대 정화 단계입니다.", ephemeral=True)
            return
        self.territory.safety = TerritorySafety(self.territory.safety.value + 1)
        self.territory.push()
        
        await interaction.response.send_message(f"성공적으로 **{self.territory.name}** 영토를 정화했습니다!", ephemeral=True)
        
        main_db.connection.commit()

class BuildButton(TerritoryLookupButton):
    
    def __init__(self, prev_interaction:discord.Interaction, building_category:discord.app_commands.Choice[int], building_name:str):
        super().__init__()
        self.prev_interaction = prev_interaction
        self.building_category = building_category
        self.building_name = building_name
        
    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.id != self.prev_interaction.user.id: raise warnings.ImpossibleToInterrupt()
        
        self.territory.set_database(main_db)
        
        if self.territory.remaining_space == 0: raise warnings.NoSpace()

        category = BuildingCategory(self.building_category.value)
        
        building = Building(
            faction_id=self.faction.id,
            territory_id=self.territory.id,
            category=category,
            name=self.building_name
        )
        
        building.set_database(main_db)
        building.push()
        
        await interaction.response.send_message(f"성공적으로 **{self.building_name}** 건물을 건설했습니다!", ephemeral=True)
        
        main_db.connection.commit()

# 세력 해산 버튼
class FactionDeleteButton(FactionLookupButton):

    def __init__(self, bot:BotBase):
        super().__init__()
        self.bot = bot
        self.style = discord.ButtonStyle.danger
    
    async def callback(self, interaction:discord.Interaction):
        # hierarchy 제거
        main_db.connection.execute(
            f"DELETE FROM FactionHierarchyNode WHERE higher = {self.faction.id} OR lower = {self.faction.id}"
        )

        # 세력 해산
        self.faction.delete()

        self.disabled = True

        await interaction.response.edit_message(view = self.view)

        await interaction.followup.send(f"{self.faction.name} 세력이 해산되었습니다.", ephemeral = True)

        await self.bot.announce(
            f"**{interaction.user.display_name}**님께서 **{self.faction.name}** 세력을 해산하셨습니다.",
            interaction.guild.id
        )
        main_db.connection.commit()


# 범용 열람 버튼 ui
class TableObjectView(View):

    def __init__(
            self, 
            fetch_list:list[TableObject], 
            button: TableObjectButton
        ):
        """
        fetch_list : 테이블 객체 리스트, 즉 list[TableObject]
        display_column : 버튼에 표시할 데이터의 컬럼 이름 (None일 경우 ID로 대체)
            출력 양식은 "%s (ID : %d)" 형태, 이름이 None일 경우 "%d" 형태
        button_class : 버튼 클래스 객체, GeneralLookupButton을 상속받아야 함
        kwargs : button_class에 넘겨줄 인자 (bot 등)
        """
        super().__init__(timeout = 180)
        
        if not issubclass(type(button), TableObjectButton):
            raise TypeError("button_class는 GeneralLookupButton을 상속받아야 합니다.")

        if not fetch_list:
            self.add_item(NoDataButton())
            return

        for tableobj in fetch_list:
            self.add_item(button.set_table_object(tableobj).build())

class SelectView(View):
    
    def __init__(self, select, *, timeout = 180):
        super().__init__(timeout = timeout)
        self.add_item(select)

# 테스트

class test_button(View):
    def __init__(self, *, timeout = 30):
        super().__init__(timeout = timeout)
    
    @ui.button(label = "눌러봐!!", style=discord.ButtonStyle.primary, emoji="\U0001f974")
    async def test(self, interaction:discord.Interaction, button:discord.Button):
        button.disabled = True
        button.label = "눌렸어!"
        await interaction.response.edit_message(content = "버튼이 눌렸어!", view = self)

class test_select(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label = "선택지1", value = "1"),
            discord.SelectOption(label = "선택지2", value = "2"),
            discord.SelectOption(label = "선택지3", value = "3")
        ]
        super().__init__(placeholder = "선택해봐!", min_values = 1, max_values = 1, options = options)
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(f"선택지 {nominative(self.values[0])} 선택되었어!", ephemeral = True)

class test_select_view(View):
    def __init__(self, *, timeout = 30):
        super().__init__(timeout = timeout)
        self.add_item(test_select())