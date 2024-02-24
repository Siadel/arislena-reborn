import discord
from discord.ui import View, Button
from discord import ui, Colour

from py_discord.embeds import table_info
from py_discord.bot_base import BotBase
from py_base.koreanstring import nominative
from py_system.global_ import main_db
from py_system.tableobj import TableObject, User, Faction, Territory

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
        
class GeneralLookupButton(Button):
    
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
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(
            embed = table_info(
                discord.Embed(title = f"{self.label_txt} 정보", color = Colour.green()), 
                self.table_object
            ),
            ephemeral = True)
        
class UserLookupButton(GeneralLookupButton):

    def __init__(self, user:User, bot:BotBase, interaction:discord.Interaction):
        member = discord.utils.get(interaction.guild.members, id = user.discord_id)
        super().__init__(
            user, 
            bot = bot, 
            label_complementary = f"{member.display_name}"
        )
        self.interaction = interaction

class FactionLookupButton(GeneralLookupButton):

    def __init__(self, faction:Faction, bot:BotBase, interaction:discord.Interaction):
        user = discord.utils.get(interaction.guild.members, id = faction.user_id)
        super().__init__(
            faction, 
            bot = bot, 
            label_complementary = f"소유자 : {user.display_name}"
        )
        self.interaction = interaction

class TerritoryLookupButton(GeneralLookupButton):

    def __init__(self, territory:Territory, bot:BotBase, interaction:discord.Interaction):
        faction = Faction.from_database(main_db, id = territory.faction_id)
        super().__init__(
            territory, 
            bot = bot, 
            label_complementary = f"소유 세력 : {faction.name}"
        )
        self.interaction = interaction

# 세력 해산 버튼
class FactionDeleteButton(GeneralLookupButton):

    def __init__(self, faction:Faction, bot:BotBase):
        super().__init__(faction, bot = bot)
        self.style = discord.ButtonStyle.danger
        self.faction:Faction = faction
    
    async def callback(self, interaction:discord.Interaction):
        # hierarchy 제거
        main_db.connection.execute(
            f"DELETE FROM FactionHierarchy WHERE higher = {self.faction.id} OR lower = {self.faction.id}"
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


# 범용 열람 버튼 ui
class LookupView(View):

    def __init__(
            self, 
            fetch_list:list, 
            *, 
            timeout = 180, 
            button_class = GeneralLookupButton, 
            **kwargs
        ):
        """
        fetch_list : 테이블 객체 리스트, 즉 list[TableObject] (fetch_all로 가져온 것)
        display_column : 버튼에 표시할 데이터의 컬럼 이름 (None일 경우 ID로 대체)
            출력 양식은 "%s (ID : %d)" 형태, 이름이 None일 경우 "%d" 형태
        button_class : 버튼 클래스 객체, GeneralLookupButton을 상속받아야 함
        kwargs : button_class에 넘겨줄 인자 (bot 등)
        """
        super().__init__(timeout = timeout)
        
        if button_class and not issubclass(button_class, GeneralLookupButton):
            raise TypeError("button_class는 GeneralLookupButton을 상속받아야 합니다.")

        if not fetch_list:
            self.add_item(NoDataButton())
            return

        for tableobj in fetch_list:
            self.add_item(button_class(tableobj, **kwargs))

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