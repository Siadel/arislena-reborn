import discord
from discord.ui import View, Button
from discord import ui, Colour

from py_base.koreanstring import nominative
from py_base.ari_enum import BuildingCategory, TerritorySafety
from py_system._global import main_db
from py_system.tableobj import TableObject, User, Faction, Territory, Building, Crew
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
    
    def __init__(
            self, 
            table_object:TableObject, 
            *,
            bot:BotBase = None,
            label_complementary:str = None
        ):
        """
        table_object : 테이블 객체
        sub : {"key" : value} 형태의 딕셔너리, 테이블 객체의 서브 테이블을 가져올 때 사용
            ex) {"user_ID" : 1234567890}
        """
        display_value = getattr(table_object, table_object.display_column, "-")

        label_txt = f"{display_value}"
        if label_complementary: label_txt += f" ({label_complementary})"
        # <메인으로 출력할 데이터> (<서브로 보여줄 데이터 컬럼 한국어명> : <서브로 출력할 데이터>) 형태
        super().__init__(label = label_txt, style = discord.ButtonStyle.primary)

        self.table_object = table_object
        self.label_txt = label_txt
        self.bot = bot
    
    def _get_basic_embed(self):
        return table_info(
            discord.Embed(title = f"{self.label_txt} 정보", color = Colour.green()), 
            self.table_object
        )
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(
            embed = self._get_basic_embed(),
            ephemeral = False # 일단은 False로
        )
        
class UserLookupButton(TableObjectButton):

    def __init__(self, user:User, bot:BotBase, interaction:discord.Interaction):
        member = discord.utils.get(interaction.guild.members, id = user.discord_id)
        super().__init__(
            user, 
            bot = bot, 
            label_complementary = f"{member.display_name}"
        )

class FactionLookupButton(TableObjectButton):

    def __init__(self, faction:Faction, bot:BotBase, interaction:discord.Interaction):
        user = discord.utils.get(interaction.guild.members, id = faction.user_id)
        super().__init__(
            faction, 
            bot = bot, 
            label_complementary = f"소유자 : {user.display_name}"
        )

class TerritoryLookupButton(TableObjectButton):

    def __init__(self, territory:Territory, bot:BotBase):
        self.faction = Faction.from_database(main_db, id = territory.faction_id)
        super().__init__(
            territory, 
            bot = bot, 
            label_complementary = f"소유 세력 : {self.faction.name}"
        )
    
    async def callback(self, interaction:discord.Interaction):
        embed = self._get_basic_embed()
        # 건물 정보 추가
        buildings = main_db.fetch_many("building", territory_id = self.table_object.id)
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
    
    def __init__(self, crew:Crew, bot:BotBase):
        # faction = Faction.from_database(main_db, id = crew.faction_id)
        super().__init__(
            crew, 
            bot = bot,
            label_complementary = f"아이디 : {crew.id}"
        )
        self.crew = crew

class CrewNameButton(CrewLookupButton):
    
    async def callback(self, interaction:discord.Interaction):
        
        await interaction.response.send_modal(modals.NameCrew(bot = self.bot, previous_crew_name = self.crew.name))

class PurifyButton(TerritoryLookupButton):
    
    def __init__(self, territory:Territory, bot:BotBase, prev_interaction:discord.Interaction):
        super().__init__(territory, bot = bot)
        self.table_object = territory
        self.prev_interaction = prev_interaction
    
    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.id != self.prev_interaction.user.id: raise warnings.ImpossibleToInterrupt()
        
        self.table_object.set_database(main_db)
        
        if self.table_object.safety.value == TerritorySafety.max_value():
            await interaction.response.send_message("이미 최대 정화 단계입니다.", ephemeral=True)
            return
        self.table_object.safety = TerritorySafety(self.table_object.safety.value + 1)
        self.table_object.push()
        
        await interaction.response.send_message(f"성공적으로 **{self.table_object.name}** 영토를 정화했습니다!", ephemeral=True)
        
        main_db.connection.commit()

class BuildButton(TerritoryLookupButton):
    
    def __init__(self, territory:Territory, bot:BotBase, prev_interaction:discord.Interaction, building_category:discord.app_commands.Choice[int], building_name:str):
        super().__init__(territory, bot = bot)
        self.table_object = territory
        self.prev_interaction = prev_interaction
        self.building_category = building_category
        self.building_name = building_name
        
    async def callback(self, interaction:discord.Interaction):
        
        if interaction.user.id != self.prev_interaction.user.id: raise warnings.ImpossibleToInterrupt()
        
        self.table_object.set_database(main_db)
        
        if self.table_object.remaining_space == 0: raise warnings.NoSpace()

        category = BuildingCategory(self.building_category.value)
        
        building = Building(
            territory_id=self.table_object.id,
            category=category,
            name=self.building_name
        )
        
        Building.set_database(main_db)
        building.push()
        
        await interaction.response.send_message(f"성공적으로 **{self.building_name}** 건물을 건설했습니다!", ephemeral=True)
        
        main_db.connection.commit()

# 세력 해산 버튼
class FactionDeleteButton(TableObjectButton):

    def __init__(self, faction:Faction, bot:BotBase):
        super().__init__(faction, bot = bot)
        self.style = discord.ButtonStyle.danger
        self.faction:Faction = faction
    
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
            *, timeout = 180, 
            button_class = TableObjectButton, 
            **button_class_param
        ):
        """
        fetch_list : 테이블 객체 리스트, 즉 list[TableObject]
        display_column : 버튼에 표시할 데이터의 컬럼 이름 (None일 경우 ID로 대체)
            출력 양식은 "%s (ID : %d)" 형태, 이름이 None일 경우 "%d" 형태
        button_class : 버튼 클래스 객체, GeneralLookupButton을 상속받아야 함
        kwargs : button_class에 넘겨줄 인자 (bot 등)
        """
        super().__init__(timeout = timeout)
        
        if button_class and not issubclass(button_class, TableObjectButton):
            raise TypeError("button_class는 GeneralLookupButton을 상속받아야 합니다.")

        if not fetch_list:
            self.add_item(NoDataButton())
            return

        for tableobj in fetch_list:
            self.add_item(button_class(tableobj, **button_class_param))

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