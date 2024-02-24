import discord
from discord.ext import commands
from discord import app_commands
from py_base.jsonwork import dump_json

from py_discord.bot_base import BotBase
from py_discord import warnings
from py_system import arislena_dice, arislena_dice_extension
from py_system.global_ import dice_memory

# arislena_dice 모듈에 선언된 모든 주사위 객체를 불러옴
dice_list = arislena_dice.indipendent_dice_list + arislena_dice.group_only_dice_list
dice_choice = [app_commands.Choice(name=dice.category, value=dice.category) for dice in dice_list]
# indipendent_dice_list만 등록 가능함
dice_choice_for_register = [app_commands.Choice(name=dice.category, value=dice.category) for dice in arislena_dice.indipendent_dice_list]

def find_dice(dice_category: str) -> arislena_dice.Dice:
    for dice in dice_list:
        if dice.category == dice_category:
            return dice
    raise Exception(f"주사위를 찾을 수 없습니다. ({dice_category})")

# 주사위 시행 엠베드 생성 함수
def create_dice_embed(dice:arislena_dice.Dice, more_information:bool):

    embed = discord.Embed(
        title = "주사위 굴리기 결과",
        color = discord.Color.green()
    )
    embed.add_field(name="주사위 종류", value=dice.category, inline=False)
    if dice.name: embed.add_field(name="주사위 이름", value=dice.name, inline=False)
    embed.add_field(name="주사위 숫자", value=dice.last_roll)
    embed.add_field(name="주사위 등급", value=dice.last_grade)
    embed.add_field(name="주사위 판정", value=dice.last_judge)

    # 확장된 주사위인 경우, 확장된 주사위 등급과 판정 출력
    if isinstance(dice, arislena_dice_extension.FixerConditionDice):
        embed.add_field(name="확장 주사위 등급", value=dice.last_extended_grade)
        embed.add_field(name="확장 주사위 판정", value=dice.last_extended_judge)

    # 이벤트 주사위를 굴리면서 티어를 입력한 경우, 티어값 출력
    if type(dice) == arislena_dice.Nonahedron and (dice.h_tier and dice.l_tier and dice.s_tier):
        embed.add_field(name="고점 중시 티어", value=dice.h_tier)
        embed.add_field(name="저점 극복 티어", value=dice.l_tier)
        embed.add_field(name="안정 중시 티어", value=dice.s_tier)
    
    # 추가 정보 선택 시, 주사위에 대한 추가 정보 출력
    if more_information:
        embed.add_field(name="주사위 등급 테이블", value=dice.grade_table, inline=False)
        embed.add_field(name="주사위 판정 테이블", value=dice.judge_table, inline=False)
    
    return embed

class dice_package(commands.GroupCog, name="주사위"):
    def __init__(self, bot: BotBase):
        self.bot = bot
        super().__init__()

    @app_commands.command(
        name = "등록",
        description = "원하는 종류의 주사위를 이름을 붙여 등록합니다. 같은 이름으로 주사위를 등록하면, 주사위가 덮어씌워집니다. 출산, 환경 주사위는 등록이 불가능합니다."
    )
    @app_commands.describe(
        dice_category = "주사위 유형 선택",
        dice_name = "주사위 이름",
        dice_mod = "주사위 숫자에 더해질 값"
    )
    @app_commands.choices(
        dice_category = dice_choice_for_register
    )
    async def register_dice(
        self, interaction: discord.Interaction,
        dice_category: app_commands.Choice[str],
        dice_name: str,
        dice_mod: int = 0
    ):
        # 주사위 등록

        # 그룹 주사위
        registered_dice:arislena_dice.Dice = find_dice(dice_category.value)(dice_mod)
        
        registered_dice.name = dice_name
        dice_memory.update_a_key(dice_name, registered_dice.__dict__)

        # 등록한 주사위의 종류, 이름, dice_mod, grade_mod를 출력하는 embed 생성
        embed = discord.Embed(
            title = "주사위 등록 결과",
            color = discord.Color.green()
        )
        embed.add_field(name="주사위 종류", value=registered_dice.category, inline=False)
        embed.add_field(name="주사위 이름", value=registered_dice.name, inline=False)
        # embed.add_field(name="주사위 눈 보정치", value=registered_dice.dice_mod, inline=False)
        # embed.add_field(name="주사위 등급 보정치", value=registered_dice.grade_mod, inline=False)

        await interaction.response.send_message(embed=embed)
    
    # @app_commands.command(
    #     name = "수정",
    #     description = "등록한 주사위의 상세 정보를 설정합니다."
    # )
    # @app_commands.describe(
    #     dice_name = "등록한 주사위 이름",
    # )
    # async def modify_dice(
    #     self, interaction: discord.Interaction,
    # ):
    #     pass

    @app_commands.command(
        name = "목록",
        description = "등록한 주사위 목록을 출력합니다."
    )
    async def show_dice_list(self, interaction: discord.Interaction):
        registered_dice_list = list(dice_memory.__dict__.keys())

        # 등록한 주사위의 이름을 출력하는 embed 생성
        
        embed = discord.Embed(
            title = "주사위 목록",
            color = discord.Color.green()
        )
        if len(registered_dice_list) == 0:
            embed.add_field(name="주사위 목록", value="등록된 주사위가 없습니다.", inline=False)
        else:
            for number, dice_name in enumerate(registered_dice_list.keys(), start=1):
                embed.add_field(name=f"{number}. {dice_name}", value=registered_dice_list[dice_name]["category"], inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name = "시행",
        description = "등록한 주사위를 굴리고, 시행 결과를 출력합니다. 주사위 즉시 보정치와, 티어값을 입력할 수 있습니다."
    )
    @app_commands.describe(
        dice_name = "등록한 주사위 이름",
        immediate_dice_mod = "이번 시행에 굴릴 주사위에 한해 더해질 값",
        more_information = "주사위에 대한 추가 정보(등급 테이블, 판정 테이블 정보)"
    )
    async def roll_a_dice(
        self, interaction: discord.Interaction,
        dice_name: str,
        immediate_dice_mod: int = 0,
        more_information: bool = False
    ):
        # 주사위 불러오기
        registered_dice_data = dice_memory.get(dice_name)
        registered_dice = find_dice(registered_dice_data["category"]).from_dice_data(registered_dice_data)

        # 이벤트 주사위를 굴릴 경우
        if isinstance(registered_dice, arislena_dice.Nonahedron):
            # 티어에 따른 주사위 보정치 적용
            registered_dice.apply_tier()

        # 주사위 굴리기
        registered_dice.roll(immediate_dice_mod)

        # 주사위 저장
        dice_memory.update_a_key(dice_name, registered_dice.__dict__)
        dump_json(dice_memory.to_json(), "dice_memory.json")

        # embed 생성
        embed = create_dice_embed(registered_dice, more_information)

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(
        name = "그룹시행",
        description = "등록한 그룹 주사위를 굴리고, 시행 결과를 출력합니다. 그룹 주사위는 보정치를 입력할 수 없습니다."
    )
    @app_commands.describe(
        dice_name = "등록한 주사위 이름"
    )
    async def roll_a_group_dice(
        self, interaction: discord.Interaction,
        dice_name: str
    ):
        pass
    
    @app_commands.command(
        name = "삭제",
        description = "등록한 주사위를 삭제합니다."
    )
    @app_commands.describe(
        dice_name = "등록한 주사위 이름"
    )
    async def delete_a_dice(
        self, interaction: discord.Interaction,
        dice_name: str
    ):
        dice_memory.delete_a_key(dice_name)

        embed = discord.Embed(
            title = "주사위 삭제 결과",
            color = discord.Color.green()
        )
        embed.add_field(name="주사위 이름", value=dice_name, inline=False)
        embed.add_field(name="결과", value="성공적으로 삭제되었습니다.", inline=False)

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(
        name = "비교",
        description = "등록한 두 주사위의 격차를 출력합니다. 두 주사위의 분류가 다를 경우, 비교가 불가능합니다."
    )
    @app_commands.describe(
        first_dice_name = "등록한 주사위 이름",
        second_dice_name = "등록한 주사위 이름",
    )
    async def compare_two_dice(
        self, interaction: discord.Interaction,
        first_dice_name: str,
        second_dice_name: str
    ):
        if first_dice_name == second_dice_name: raise warnings.Default("같은 이름의 주사위를 비교할 수 없습니다.")

        dice_1_data = dice_memory.get(first_dice_name)
        dice_2_data = dice_memory.get(second_dice_name)

        dice_1 = find_dice(dice_1_data["category"]).from_dice_data(dice_1_data)
        dice_2 = find_dice(dice_2_data["category"]).from_dice_data(dice_2_data)

        if not dice_1.comparable or not dice_2.comparable: raise warnings.Default("비교할 수 없는 주사위입니다.")

        compare_result = dice_1.compare_gap_str(dice_2)

        embed = discord.Embed(
            title = "주사위 비교 결과",
            color = discord.Color.green()
        )
        embed.add_field(name="비교 구도", value=f"{first_dice_name} vs {second_dice_name}", inline=False)
        embed.add_field(name="주사위 분류", value=dice_1.category, inline=False)
        embed.add_field(name="결과", value=compare_result, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name = "총분석",
        description = "등록된 총분석 주사위를 모두 비교한 결과를 출력합니다."
    )
    async def compare_advantage_dice(
        self, interaction: discord.Interaction
    ):
        pass
    
    @app_commands.command(
        name = "바로시행",
        description = "등록되지 않은 주사위를 굴리고, 시행 결과를 출력합니다."
    )
    @app_commands.describe(
        dice_category = "주사위 종류 선택",
        dice_mod = "주사위 숫자에 더해질 값",
        grade_mod = "등급값에 더해질 값",
        immediate_dice_mod = "이번 시행에 굴릴 주사위에 한해 더해질 값",
        embed_ephemeral = "시행 결과를 숨길지 여부",
        more_information = "주사위에 대한 추가 정보(등급 테이블, 판정 테이블 정보)를 출력할지 여부"
    )
    @app_commands.choices(
        dice_category = dice_choice
    )
    async def roll_a_dice_without_register(
        self, interaction: discord.Interaction,
        dice_category: app_commands.Choice[str],
        dice_mod: int = 0,
        grade_mod: int = 0,
        immediate_dice_mod: int = 0,
        embed_ephemeral: bool = False,
        more_information: bool = False
    ):
        new_dice:arislena_dice.Dice = find_dice(dice_category.value)

        # 주사위 굴리기
        if new_dice in arislena_dice.indipendent_dice_list:
            new_dice = new_dice()
            new_dice.dice_mod = dice_mod
            new_dice.grade_mod = grade_mod
            new_dice.roll(immediate_dice_mod)

            embed = create_dice_embed(new_dice, more_information)

            await interaction.response.send_message(embed=embed, ephemeral=embed_ephemeral)
        elif new_dice in arislena_dice.group_only_dice_list:
            embeds = []
            for sub_dice in new_dice.__subclasses__():
                sub_dice = sub_dice()
                sub_dice.roll(immediate_dice_mod)

                embeds.append(create_dice_embed(sub_dice, more_information))

            await interaction.response.send_message(embeds=embeds, ephemeral=embed_ephemeral)

    
async def setup(bot: BotBase):
    await bot.add_cog(dice_package(bot), guilds=bot.objectified_guilds)