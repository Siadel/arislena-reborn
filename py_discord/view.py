import discord
from discord import ui

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