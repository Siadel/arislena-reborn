import discord
from discord import ui, Colour

from py_discord.embed import table_info
from py_base.koreanstring import nominative
from py_system import tableobj

# /유저 설정 - 설정 정보 출력
# 설정의 한국어명과 설정값 출력
# 설정값을 바꾸는 것으로 실제 설정을 바꿀 수 있어야 함

class user_setting_view(ui.View):

    def __init__(self, user_setting:tableobj.User_setting, *, timeout = 180):
        super().__init__(timeout = timeout)
        self.user_setting = user_setting

        for key, value in user_setting.kr_dict_without_id.items():
            self.add_item(user_setting_button(key, value))
    
    @ui.button(label = "닫기", style = discord.ButtonStyle.danger)
    async def close(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.edit_message(content = "설정 닫힘", view = None)

class user_setting_button(ui.Button):

    def __init__(self, key:str, value:str):
        super().__init__(label = key, style = discord.ButtonStyle.secondary)
        self.key = key
        self.value = value
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(f"{self.key} : **{self.value}**", ephemeral = True)

# 범용 데이터 없음 표시 버튼
class NoDataButton(ui.Button):

    def __init__(self, *, style = discord.ButtonStyle.danger):
        super().__init__(label = "데이터 없음", style = style, disabled = True)
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message("데이터 없음", ephemeral = True)

# 범용 열람 버튼 ui
# 인자로 table 이름을 받아서 해당 테이블의 name column과 ID column을 출력
# 출력 양식은 "이름 (ID : %d)" 형태
        
class GeneralLookupButton(ui.Button):
    
    def __init__(self, tableobj:tableobj.TableObject, display_column:str = None):
        """
        tableobj : 테이블 객체
        display_column : 버튼에 표시할 데이터의 컬럼 이름 (None일 경우 ID로 대체)
            출력 양식은 "%s (ID : %d)" 형태, 이름이 None일 경우 "%d" 형태
        """
        label_txt = f"{tableobj.__getattribute__(display_column)} (ID : {tableobj.ID})" if display_column else f"{tableobj.ID}"
        super().__init__(label = label_txt, style = discord.ButtonStyle.primary)
        self.tableobj = tableobj
        self.label_txt = label_txt
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(embed = table_info(
            discord.Embed(title = f"{self.label_txt} 정보", color = Colour.green()), self.tableobj
        ), ephemeral = True)

class FactionDeleteButton(GeneralLookupButton):

    def __init__(self, tableobj:tableobj.TableObject):
        super().__init__(tableobj, "name")
        self.style = discord.ButtonStyle.danger
    
    async def callback(self, interaction:discord.Interaction):
        pass
        # 실제 삭제 구현

class GeneralLookupView(ui.View):

    def __init__(self, fetch_list:list, *, display_column:str = None, button_class = GeneralLookupButton, timeout = 180):
        """
        fetch_list : 테이블 객체 리스트, 즉 list[TableObject] (fetch_all로 가져온 것)
        display_column : 버튼에 표시할 데이터의 컬럼 이름 (None일 경우 ID로 대체)
            출력 양식은 "%s (ID : %d)" 형태, 이름이 None일 경우 "%d" 형태
        button_class : 버튼 클래스 객체, GeneralLookupButton을 상속받아야 함
        """
        super().__init__(timeout = timeout)
        
        if button_class and not issubclass(button_class, GeneralLookupButton):
            raise TypeError("button_class는 GeneralLookupButton을 상속받아야 합니다.")

        if not fetch_list:
            self.add_item(NoDataButton())
            return

        for tableobj in fetch_list:
            self.add_item(button_class(tableobj, display_column))

# 테스트

class test_button(ui.View):
    def __init__(self, *, timeout = 30):
        super().__init__(timeout = timeout)
    
    @ui.button(label = "눌러봐!!", style=discord.ButtonStyle.primary, emoji="\U0001f974")
    async def test(self, interaction:discord.Interaction, button:discord.ui.Button):
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

class test_select_view(ui.View):
    def __init__(self, *, timeout = 30):
        super().__init__(timeout = timeout)
        self.add_item(test_select())