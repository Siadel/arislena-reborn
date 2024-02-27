import discord
from discord.ui import Modal, TextInput

from py_discord import warnings
from py_discord import func
from py_discord.bot_base import BotBase
from py_system.tableobj import Faction, FactionHierarchyNode, Territory
from py_system.global_ import main_db, name_regex, game_setting

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

    faction_name = TextInput(
        label="세력명",
        min_length=1,
        max_length=game_setting.name_length_limit,
        placeholder="한글, 다이어크리틱 없는 영문, 숫자, 공백만 허용됩니다.",
        style=discord.TextStyle.short
    )
    
    def __init__(self, *, bot:BotBase = None):
        super().__init__(title="세력 창설")
        self.bot = bot

    async def on_submit(self, interaction:discord.Interaction):

        faction_name = self.faction_name.value.strip()
        # 특수문자가 포함되어 있는지 확인
        func.check_special_character_and_raise(faction_name)

        # 세력 데이터베이스에 추가
        new_faction = Faction(user_id=interaction.user.id, name=faction_name)
        new_faction.set_database(main_db)
        new_faction.push()

        # id가 가장 낮은 세력의 하위 세력으로 설정
        optimal_faction = Faction.from_database(main_db, "id = (SELECT MIN(id) FROM faction)")
        new_fhn = FactionHierarchyNode()
        new_fhn.set_database(main_db)
        new_fhn.push(new_faction, optimal_faction)

        main_db.connection.commit()

        await interaction.response.send_message(f"성공적으로 세력을 창설했습니다!", ephemeral=True)
        
        await self.bot.announce(f"**{interaction.user.display_name}**님께서 **{self.faction_name}** 세력을 창설했어요!", interaction.guild.id)

class NewTerritoryModal(ArislenaGeneralModal):

    territory_name = TextInput(
        label="영토 이름",
        min_length=1,
        max_length=30,
        placeholder="한글, 다이어크리틱 없는 영문, 숫자, 공백만 허용됩니다.",
        style=discord.TextStyle.short
    )

    def __init__(self, *, bot:BotBase = None):
        super().__init__(title="새 영토예요!")
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction) -> None:
        
        territory_name = self.territory_name.value.strip()
        # 특수문자가 포함되어 있는지 확인
        func.check_special_character_and_raise(territory_name)

        # 세력 데이터베이스에 추가
        faction = Faction.from_database(main_db, user_id=interaction.user.id)
        # 새 영토 생성
        t = Territory(faction_id=faction.id, name=territory_name)
        t.explicit_post_init()
        t.set_database(main_db)
        t.push()

        main_db.connection.commit()

        await interaction.response.send_message(f"성공적으로 **{territory_name}** 영토를 생성했습니다!", ephemeral=True)
