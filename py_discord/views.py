import discord
from discord.ui import View, Button
from discord import ui
from typing import Any

from py_base.koreanstring import nominative
from py_base.ari_enum import BuildingCategory, TerritorySafety, ResourceCategory
from py_system.tableobj import TableObject, User, Faction, Territory, Building, Resource
from py_system.systemobj import Crew, SystemBuilding
from py_discord import warnings, modals, embeds
from py_discord.bot_base import BotBase
from py_discord.abstract import TableObjectButton

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

# 범용 취소 버튼
class CancelButton(Button):
    
    def __init__(self, *, style = discord.ButtonStyle.danger):
        super().__init__(label = "취소", style = style)
        
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.edit_message(content = "작업이 취소되었습니다.", view = None)

# 범용 열람 버튼
# 인자로 table 이름을 받아서 해당 테이블의 name column과 ID column을 출력
# 출력 양식은 "이름 (ID : %d)" 형태


class UserLookupButton(TableObjectButton):
    
    corr_obj_type = User

    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction):
        super().__init__(bot, interaction_for_this)
        self.user: User = None
        
    def clone(self):
        return UserLookupButton(self._bot, self._interaction_for_this)
        
    def _check_type(self, user: User | Any):
        super()._check_type(user)
        
    def _set_label_complementary(self, user: User):
        member = discord.utils.get(self._interaction_for_this.guild.members, id = user.discord_id)
        self.label_complementary = f"{member.display_name}"
    
    def set_table_object(self, user: User):
        self.user = user
        return super().set_table_object(user)

class FactionLookupButton(TableObjectButton):
    
    corr_obj_type = Faction

    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction):
        super().__init__(bot, interaction_for_this)
        self.faction: Faction = None
        
    def clone(self):
        return FactionLookupButton(self._bot, self._interaction_for_this)
        
    def _check_type(self, faction: Faction | Any):
        super()._check_type(faction)
    
    def _set_label_complementary(self, faction: Faction):
        user = discord.utils.get(self._interaction_for_this.guild.members, id = faction.user_id)
        self.label_complementary = f"소유자 : {user.display_name}"
        
    def set_table_object(self, faction: Faction):
        self.faction = faction
        return super().set_table_object(faction)
    
    async def callback(self, interaction: discord.Interaction[discord.Client]):
        embed = self._get_basic_embed()
        
        # 자원 상황 출력
        field_values = []
        for resource_category in ResourceCategory.to_list():
            resource = Resource.from_database(
                self._database, faction_id = self.faction.id, category = resource_category
            )
            field_values.append(resource.to_embed_value())
        
        embed.add_field(
            name="자원 현황",
            value="\n".join(field_values)
        )
        
        await interaction.response.send_message(
            embed = embed,
            ephemeral = False
        )

class TerritoryLookupButton(TableObjectButton):
    
    corr_obj_type = Territory

    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction, faction:Faction):
        super().__init__(bot, interaction_for_this)
        self._faction = faction
        self._territory: Territory = None
        
    def clone(self):
        return TerritoryLookupButton(self._bot, self._interaction_for_this, self._faction)
        
    def _check_type(self, territory: Territory | Any):
        super()._check_type(territory)
    
    def _set_label_complementary(self, territory: Territory):
        self.label_complementary = f"{territory.safety.emoji}"
    
    def set_table_object(self, territory: Territory):
        self._territory = territory
        return super().set_table_object(territory)
    
    async def callback(self, interaction:discord.Interaction):
        embed = self._get_basic_embed()
        field_value = ""
        # 건물 정보 추가
        
        if (b_datas := self._database.fetch_many(Building.get_table_name(), territory_id = self._territory.id)):
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
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction):
        super().__init__(bot, interaction_for_this)
        self._crew: Crew = None
        
    def clone(self):
        return CrewLookupButton(self._bot, self._interaction_for_this)
        
    def _check_type(self, crew: Crew | Any):
        super()._check_type(crew)
        
    def _set_label_complementary(self, crew: Crew):
        self.label_complementary = f"{crew.id}"
        
    def set_table_object(self, crew: Crew):
        self._crew = crew
        self._crew.set_database(self._database)
        return super().set_table_object(crew)
    
    async def callback(self, interaction:discord.Interaction):
        embed = embeds.CrewLookupEmbed(
            self._crew, 
            self._database, 
            self._bot.get_server_manager(self._interaction_for_this.guild_id).table_obj_translator
        )\
            .add_basic_field()\
            .add_location_field()\
            .add_experience_field()\
            .add_description_field()
        
        await interaction.response.send_message(
            embed = embed,
            ephemeral = False
        )

class CrewDismissButton(CrewLookupButton):
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction):
        CrewLookupButton.__init__(self, bot, interaction_for_this)
        
        self.interaction_for_this:discord.Interaction = None
        self.style = discord.ButtonStyle.danger
        
    def clone(self):
        return CrewDismissButton(self._bot, self.interaction_for_this)
    
    async def callback(self, interaction:discord.Interaction):
        self.check_interruption(interaction)
        self._crew.set_database(self._database)
        desc = self._crew.get_description()
        desc.set_database(self._database)
        exp_list = self._crew.get_every_experience()
        for exp in exp_list:
            exp.set_database(self._database)
            exp.delete()
        desc.delete()
        self._crew.delete()
        
        # 누른 버튼 비활성화
        self.disabled = True
        await interaction.response.edit_message(view = self.view)
        
        await interaction.followup.send(f"**{self._crew.name}** 대원을 해고했습니다.")
        await self._bot.announce_channel(
            f"{interaction.user.display_name}님께서 **{self._crew.name}** 대원을 해고했습니다.", 
            self._bot.get_server_manager(interaction.guild_id).guild_setting.announce_channel_id
        )
        
        self._database.connection.commit()

class BuildingLookupButton(TableObjectButton):
    
    corr_obj_type = Building
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction):
        super().__init__(bot, interaction_for_this)
        self.building: Building = None
        
    def clone(self):
        return BuildingLookupButton(self._bot, self._interaction_for_this)
        
    def _check_type(self, building: Building | Any):
        super()._check_type(building)
        
    def _set_label_complementary(self, building: Building):
        t_name = self._database.connection.execute(f"SELECT {Territory.name.name} FROM {Territory.get_table_name()} WHERE id = {building.territory_id}").fetchone()[0]
        self.label_complementary = t_name
    
    def set_table_object(self, building: Building):
        self.building = building
        self.building.set_database(self._database)
        return super().set_table_object(building)
    
    async def callback(self, interaction: discord.Interaction):
        pass

class CrewNameButton(CrewLookupButton):
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction):
        CrewLookupButton.__init__(self, bot, interaction_for_this)
        
    def clone(self):
        return CrewNameButton(self._bot, self._interaction_for_this)
    
    async def callback(self, interaction:discord.Interaction):
        self.check_interruption(interaction)
        await interaction.response.send_modal(
            modals.NameCrewModal(self._bot, self._crew.name)
        )

class SelectCrewToDeployButton(CrewLookupButton):
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction, faction:Faction):
        CrewLookupButton.__init__(self, bot, interaction_for_this)
        
        self._faction = faction
        
    def clone(self):
        return SelectCrewToDeployButton(self._bot, self._interaction_for_this, self._faction)
    
    def disable_or_not(self):
        return self._crew.is_available()
    
    async def callback(self, interaction:discord.Interaction):
        self.check_interruption(interaction)
        # deployment 가져오기
        view = TableObjectView(
            fetch_list = [Building.from_data(data) for data in self._database.fetch_many("building", faction_id = self._faction.id)],
            sample_button = DeployToBuildingButton(self._bot, interaction, self._crew, self._faction)
        )
        view.add_item(CancelButton())
        await interaction.response.send_message(
            f"**{self._crew.name}** 대원을 배치할 건물을 선택하세요.",
            view = view
        )
    

class DeployToBuildingButton(BuildingLookupButton):
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction, crew:Crew, faction:Faction):
        BuildingLookupButton.__init__(self, bot, interaction_for_this)
        
        self._crew = crew
        self._faction = faction
        
    def clone(self):
        return DeployToBuildingButton(self._bot, self._interaction_for_this, self._crew, self._faction)
        
    def disable_or_not(self):
        self.disabled = not self.building.is_deployable()
    
    async def callback(self, interaction: discord.Interaction):
        self.check_interruption(interaction)
        
        self.building.set_database(self._database)
        self.building.deploy(self._crew)
        
        await interaction.response.send_message(
            f"**{self._crew.name}** 대원을 **{self.building.name}** ({self.building.category.express()}) 건물에 배치했습니다!"
        )
        
        self._database.connection.commit()

class PurifyButton(TerritoryLookupButton):
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction, faction: Faction):
        super().__init__(bot, interaction_for_this, faction)
    
    def clone(self):
        return PurifyButton(self._faction, self._bot, self._interaction_for_this)
            
    def disable_or_not(self):
        if self._territory.safety == TerritorySafety.get_max_safety(): self.disabled = True
    
    async def callback(self, interaction:discord.Interaction):
        self.check_interruption(interaction)
        self._territory.set_database(self._database)
        
        # if self.territory.safety.value == TerritorySafety.max_value():
        #     await interaction.response.send_message("이미 최대 정화 단계입니다.", ephemeral=True)
        #     return
        self._territory.safety = TerritorySafety(self._territory.safety.value + 1)
        self._territory.push()
        
        await interaction.response.send_message(f"성공적으로 **{self._territory.name}** 영토를 정화했습니다!", ephemeral=True)
        
        self._database.connection.commit()

class BuildButton(TerritoryLookupButton):
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction, faction: Faction,  building_category:discord.app_commands.Choice[int], building_name:str):
        super().__init__(bot, interaction_for_this, faction)
        self.building_category = building_category
        self.building_name = building_name
        self.interaction_for_this:discord.Interaction = None
        
    def clone(self):
        return BuildButton(self._bot, self._interaction_for_this, self._faction, self.building_category, self.building_name)
        
    async def callback(self, interaction:discord.Interaction):
        
        self.check_interruption(interaction)
        
        self._territory.set_database(self._database)
        
        if self._territory.remaining_space == 0: raise warnings.NoSpace()

        category = BuildingCategory(self.building_category.value)
        sys_building_type = SystemBuilding.type_from_category(category)
        
        building = Building(
            faction_id=self._faction.id,
            territory_id=self._territory.id,
            category=category,
            name=self.building_name,
            remaining_dice_cost=sys_building_type.required_dice_cost
        )
        
        building.set_database(self._database)
        building.push()
        
        await interaction.response.send_message(f"**{self.building_name}** 건물의 터를 잡았습니다! **{sys_building_type.required_dice_cost}**만큼의 주사위 총량이 요구됩니다.", ephemeral=True)
        
        self._database.connection.commit()

# 세력 해산 버튼
class FactionDeleteButton(FactionLookupButton):

    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction):
        super().__init__(bot, interaction_for_this)
        self.style = discord.ButtonStyle.danger
        
    def clone(self):
        return FactionDeleteButton(self._bot, self._interaction_for_this)
    
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

        await self._bot.announce_channel(
            f"**{interaction.user.display_name}**님께서 **{self.faction.name}** 세력을 해산하셨습니다.",
            self._bot.get_server_manager(interaction.guild_id).guild_setting.announce_channel_id
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