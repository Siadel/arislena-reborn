import discord
from discord.ui import View, Button
from discord import ui, Colour
from typing import Type, TypeVar, Any
from abc import ABCMeta, abstractmethod

from py_base.koreanstring import nominative
from py_base.ari_enum import BuildingCategory, TerritorySafety
from py_base.dbmanager import DatabaseManager
from py_system.tableobj import TableObject, User, Faction, Territory, Building, Crew, Deployment
from py_system.systemobj import SystemBuilding
from py_discord import warnings, modals
from py_discord.embeds import add_basic_table_info
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

# view 전용 추상 클래스
class BuilderPattern(metaclass=ABCMeta):
    
    def __init__(self):
        self._builded = False
    
    def build(self):
        self._builded = True
        return self

class Uninterruptable(metaclass=ABCMeta):
    
    def set_previous_interaction(self, prev_interaction:discord.Interaction):
        self.prev_interaction = prev_interaction
        return self
    
    def check_interruption(self, interaction:discord.Interaction):
        """
        view의 버튼이 다른 유저에 의해 눌렸을 때 발생하는 오류를 방지합니다.
        """
        if interaction.user.id != self.prev_interaction.user.id: raise warnings.ImpossibleToInterrupt()

class Announceable(metaclass=ABCMeta):
    
    def set_bot(self, bot:BotBase):
        self.bot = bot
        return self

# 범용 데이터 없음 표시 버튼
class NoDataButton(Button):

    def __init__(self, *, style = discord.ButtonStyle.danger):
        super().__init__(label = "데이터 없음", style = style, disabled = True)
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message("데이터 없음", ephemeral = True)

# 범용 취소 버튼
class CancelButton(Button):
    
    def __init__(self, *, style = discord.ButtonStyle.danger):
        super().__init__(label = "취소", style = style)
        
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.edit_message(content = "작업이 취소되었습니다.", view = None)

# 범용 열람 버튼
# 인자로 table 이름을 받아서 해당 테이블의 name column과 ID column을 출력
# 출력 양식은 "이름 (ID : %d)" 형태

# TableObjectButton을 상속받은 버튼에 대한 type hint
TableObjectButtonT = TypeVar("TableObjectButtonT", bound="TableObjectButton")
TableObjectT = TypeVar("TableObjectT", bound=TableObject)

class TableObjectButton(Button, BuilderPattern, metaclass=ABCMeta):
    
    corr_obj_type:Type[TableObject] = TableObject
    
    def __init__(self):
        """
        사용법:
        ```python3
        btn = TableObjectButton(...).set_table_object(table_object)
        ```
        """        
        Button.__init__(self, style = discord.ButtonStyle.primary)
        BuilderPattern.__init__(self)
        
        self._table_object: TableObject = None
        self._database: DatabaseManager = None
        self.label_complementary: str = None
        
    @abstractmethod
    def clone(self: TableObjectButtonT) -> TableObjectButtonT:
        """
        build하기 이전, 버튼의 속성을 복사한 새로운 버튼 객체를 반환
        """
        return TableObjectButton()
    
    def _get_basic_embed(self):
        return add_basic_table_info(
            discord.Embed(title = f"{self.label} 정보", color = Colour.green()), 
            self._table_object
        )
    
    def check_type(self, object: TableObjectT | Any):
        if type(object) != self.__class__.corr_obj_type:
            raise TypeError(f"{object.__class__} 클래스는 {self.__class__.corr_obj_type} 클래스의 객체와 호환되지 않습니다.")
        
    def set_database(self, database: DatabaseManager):
        self._database = database
        return self
        
    def set_label_complementary(self, table_object:TableObject):
        pass
        
    def set_table_object(self, table_object:TableObject):
        self.check_type(table_object)
        self.set_label_complementary(table_object)
        
        self._table_object = table_object
        return self
    
    def build(self):
        BuilderPattern.build(self)
        label_txt = self._table_object.get_display_string()

        if self.label_complementary: label_txt += f" ({self.label_complementary})"
        # <메인으로 출력할 데이터> (<서브로 보여줄 데이터 컬럼 한국어명> : <서브로 출력할 데이터>) 형태
        self.label = label_txt
        return self
    
    def disable_or_not(self):
        """
        이 버튼을 view에 추가하기 전에 버튼을 비활성화할지 여부를 결정합니다.
        
        이 버튼에 해당하는 객체에 대해 버튼이 정의한 행동이 불가능한 경우에 버튼을 비활성화합니다.
        """
        pass
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(
            embed = self._get_basic_embed(),
            ephemeral = False # 일단은 False로
        )



class UserLookupButton(TableObjectButton):
    
    corr_obj_type = User

    def __init__(self, prev_interaction:discord.Interaction):
        super().__init__()
        self.prev_interaction = prev_interaction
        self.user: User = None
        
    def clone(self):
        return UserLookupButton(self.prev_interaction)
        
    def check_type(self, user: User | Any):
        super().check_type(user)
        
    def set_label_complementary(self, user: User):
        member = discord.utils.get(self.prev_interaction.guild.members, id = user.discord_id)
        self.label_complementary = f"{member.nick or member.name}"
    
    def set_table_object(self, user: User):
        self.user = user
        return super().set_table_object(user)

class FactionLookupButton(TableObjectButton):
    
    corr_obj_type = Faction

    def __init__(self, prev_interaction:discord.Interaction):
        super().__init__()
        self.prev_interaction = prev_interaction
        self.faction: Faction = None
        
    def clone(self):
        return FactionLookupButton(self.prev_interaction)
        
    def check_type(self, faction: Faction | Any):
        super().check_type(faction)
    
    def set_label_complementary(self, faction: Faction):
        user = discord.utils.get(self.prev_interaction.guild.members, id = faction.user_id)
        self.label_complementary = f"소유자 : {user.display_name}"
        
    def set_table_object(self, faction: Faction):
        self.faction = faction
        return super().set_table_object(faction)

class TerritoryLookupButton(TableObjectButton):
    
    corr_obj_type = Territory

    def __init__(self, faction:Faction):
        super().__init__()
        self.faction = faction
        self.territory: Territory = None
        
    def clone(self):
        return TerritoryLookupButton(self.faction)
        
    def check_type(self, territory: Territory | Any):
        super().check_type(territory)
    
    def set_label_complementary(self, _: Territory):
        self.label_complementary = f"소유 세력 : {self.faction.name}"
    
    def set_table_object(self, territory: Territory):
        self.territory = territory
        return super().set_table_object(territory)
    
    async def callback(self, interaction:discord.Interaction):
        embed = self._get_basic_embed()
        field_value = ""
        # 건물 정보 추가
        
        if (b_datas := self._database.fetch_many(Building.__name__, territory_id = self.territory.id)):
            for b_data in b_datas:
                b_obj = Building.from_data(b_data)
                field_value += f"- {b_obj.name} ({b_obj.category.emoji} {b_obj.category.local_name})\n"
        else:
            field_value = "- 건물 없음"
        
        embed.add_field(
            name="건물 정보",
            value=field_value
        )
        
        await interaction.response.send_message(
            embed = embed,
            ephemeral = False
        )

class CrewLookupButton(TableObjectButton):
    
    corr_obj_type = Crew
    
    def __init__(self):
        super().__init__()
        self.crew: Crew = None
        
    def clone(self):
        return CrewLookupButton()
        
    def check_type(self, crew: Crew | Any):
        super().check_type(crew)
        
    def set_label_complementary(self, crew: Crew):
        self.label_complementary = f"{crew.id}"
        
    def set_table_object(self, crew: Crew):
        self.crew = crew
        self.crew.set_database(self._database)
        return super().set_table_object(crew)
    
    async def callback(self, interaction:discord.Interaction):
        embed = self._get_basic_embed()
        field_value = ""
        # 위치 정보 추가
        if (d_data := self._database.fetch(Deployment.__name__, crew_id = self.crew.id)):
            b_data = self._database.fetch(Building.__name__, id = d_data["building_id"])
            b_obj = Building.from_data(b_data)
            field_value = f"{b_obj.name} ({b_obj.category.express()})"
        else:
            field_value = "배치되지 않음"
        
        embed.add_field(
            name="위치 정보",
            value=field_value
        )
        
        await interaction.response.send_message(
            embed = embed,
            ephemeral = False
        )

class BuildingLookupButton(TableObjectButton):
    
    corr_obj_type = Building
    
    def __init__(self):
        super().__init__()
        self.building: Building = None
        
    def clone(self):
        return BuildingLookupButton()
        
    def check_type(self, building: Building | Any):
        super().check_type(building)
        
    def set_label_complementary(self, building: Building):
        self.label_complementary = building.category.express()
    
    def set_table_object(self, building: Building):
        self.building = building
        self.building.set_database(self._database)
        return super().set_table_object(building)
    
    async def callback(self, interaction: discord.Interaction):
        pass

class CrewNameButton(CrewLookupButton, Uninterruptable, Announceable):
    
    def __init__(self):
        CrewLookupButton.__init__(self)
        self.bot:BotBase = None
        self.prev_interaction:discord.Interaction = None
        
    def clone(self):
        return CrewNameButton()\
            .set_bot(self.bot)\
            .set_previous_interaction(self.prev_interaction)
    
    async def callback(self, interaction:discord.Interaction):
        self.check_interruption(interaction)
        await interaction.response.send_modal(modals.NameCrew(bot = self.bot, previous_crew_name = self.crew.name))

class SelectCrewToDeployButton(CrewLookupButton, Uninterruptable, Announceable):
    
    def __init__(self, faction:Faction):
        CrewLookupButton.__init__(self)
        self.faction = faction
        self.bot:BotBase = None
        self.prev_interaction:discord.Interaction = None
        
    def clone(self):
        return SelectCrewToDeployButton(self.faction)\
            .set_bot(self.bot)\
            .set_previous_interaction(self.prev_interaction)
    
    def disable_or_not(self):
        return self.crew.is_available()
    
    async def callback(self, interaction:discord.Interaction):
        self.check_interruption(interaction)
        # deployment 가져오기
        view = TableObjectView(
            fetch_list = [Building.from_data(data) for data in self._database.fetch_many("building", faction_id = self.faction.id)],
            sample_button = DeployToBuildingButton(self.crew, self.faction)\
                .set_database(self.bot.get_database(interaction.guild_id))\
                .set_previous_interaction(interaction)
        )
        view.add_item(CancelButton())
        await interaction.response.send_message(
            f"**{self.crew.name}** 대원을 배치할 건물을 선택하세요.",
            view = view
        )

class DeployToBuildingButton(BuildingLookupButton, Uninterruptable):
    
    def __init__(self, crew:Crew, faction:Faction):
        BuildingLookupButton.__init__(self)
        self.crew = crew
        self.faction = faction
        self.prev_interaction:discord.Interaction = None
        
    def clone(self):
        return DeployToBuildingButton(self.crew, self.faction)\
            .set_previous_interaction(self.prev_interaction)
        
    def disable_or_not(self):
        self.disabled = not self.building.is_deployable()
    
    async def callback(self, interaction: discord.Interaction):
        self.check_interruption(interaction)
        
        self.building.set_database(self._database)
        self.building.deploy(self.crew)
        
        await interaction.response.send_message(
            f"**{self.crew.name}** 대원을 **{self.building.name}** ({self.building.category.express()}) 건물에 배치했습니다!"
        )
        
        self._database.connection.commit()

class PurifyButton(TerritoryLookupButton, Uninterruptable):
    
    def __init__(self, faction:Faction):
        TerritoryLookupButton.__init__(self, faction)
        self.prev_interaction:discord.Interaction = None
    
    def clone(self):
        return PurifyButton(self.faction)\
            .set_previous_interaction(self.prev_interaction)
            
    def disable_or_not(self):
        if self.territory.safety.value == TerritorySafety.max_value(): self.disabled = True
    
    async def callback(self, interaction:discord.Interaction):
        self.check_interruption(interaction)
        self.territory.set_database(self._database)
        
        # if self.territory.safety.value == TerritorySafety.max_value():
        #     await interaction.response.send_message("이미 최대 정화 단계입니다.", ephemeral=True)
        #     return
        self.territory.safety = TerritorySafety(self.territory.safety.value + 1)
        self.territory.push()
        
        await interaction.response.send_message(f"성공적으로 **{self.territory.name}** 영토를 정화했습니다!", ephemeral=True)
        
        self._database.connection.commit()

class BuildButton(TerritoryLookupButton, Uninterruptable):
    
    def __init__(self, building_category:discord.app_commands.Choice[int], building_name:str):
        TerritoryLookupButton.__init__(self)
        self.building_category = building_category
        self.building_name = building_name
        self.prev_interaction:discord.Interaction = None
        
    def clone(self):
        return BuildButton(self.building_category, self.building_name)\
            .set_previous_interaction(self.prev_interaction)
        
    async def callback(self, interaction:discord.Interaction):
        
        self.check_interruption(interaction)
        
        self.territory.set_database(self._database)
        
        if self.territory.remaining_space == 0: raise warnings.NoSpace()

        category = BuildingCategory(self.building_category.value)
        sys_building_type = SystemBuilding.get_sys_building_type_from_category(category)
        
        building = Building(
            faction_id=self.faction.id,
            territory_id=self.territory.id,
            category=category,
            name=self.building_name,
            remaining_dice_cost=sys_building_type.required_dice_cost
        )
        
        building.set_database(self._database)
        building.push()
        
        await interaction.response.send_message(f"**{self.building_name}** 건물의 터를 잡았습니다! **{sys_building_type.required_dice_cost}**만큼의 주사위 총량이 요구됩니다.", ephemeral=True)
        
        self._database.connection.commit()

# 세력 해산 버튼
class FactionDeleteButton(FactionLookupButton, Announceable):

    def __init__(self, prev_interaction:discord.Interaction):
        FactionLookupButton.__init__(self, prev_interaction)
        self.bot:BotBase = None
        self.style = discord.ButtonStyle.danger
        
    def clone(self):
        return FactionDeleteButton(self.prev_interaction)\
            .set_bot(self.bot)
    
    async def callback(self, interaction:discord.Interaction):
        # hierarchy 제거
        self._database.connection.execute(
            f"DELETE FROM FactionHierarchyNode WHERE higher = {self.faction.id} OR lower = {self.faction.id}"
        )

        # 세력 해산
        self.faction.delete()

        self.disabled = True

        await interaction.response.edit_message(view = self.view)

        await interaction.followup.send(f"{self.faction.name} 세력이 해산되었습니다.", ephemeral = True)

        await self.bot.announce_channel(
            f"**{interaction.user.display_name}**님께서 **{self.faction.name}** 세력을 해산하셨습니다.",
            self.bot.get_server_manager(interaction.guild_id).guild_setting.announce_channel_id
        )
        self._database.connection.commit()


# 범용 열람 버튼 ui
class TableObjectView(View):

    def __init__(
            self, 
            fetch_list: list[TableObject], 
            sample_button: TableObjectButton
        ):
        """
        fetch_list : 테이블 객체의 리스트
        sample_button : 버튼 클래스 객체, TableObjectButton을 상속받아야 함. 이 클래스의 clone 메서드를 사용하여 버튼을 복사함
        """
        super().__init__(timeout = 180)
        
        if not issubclass(type(sample_button), TableObjectButton):
            raise TypeError("button 인자는 GeneralLookupButton을 상속받아야 합니다.")

        if not fetch_list:
            self.add_item(NoDataButton())
            return

        for tableobj in fetch_list:
            item = sample_button.clone()\
                .set_table_object(tableobj)\
                .build()
            item.disable_or_not()
            self.add_item(item)

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