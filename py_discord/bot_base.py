import discord
from discord.ext import commands
from discord import app_commands

from py_system import jsonobj
from py_discord import warning

# 길드 id와 봇 토큰
keys = jsonobj.Keys()

# 봇 권한 설정
intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.members = True

class BotBase(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="/",
            intents=intents,
            application_id=keys.application_id)
        
        self.token = keys.token
        self.objectified_guilds = [discord.Object(id=ID) for ID in keys.guild_ids]

    async def announce(self, message:str):
        # "아리"라는 채널에 메세지를 보냅니다.
        channel = self.get_channel(jsonobj.Settings().content["announce_channel_id"])
        await channel.send(message)

# 기능 함수들

def embed_for_user(*messages) -> discord.Embed:
    """
    유저 DM으로 보낼 embed 생성
    """

    embed = discord.Embed(title="안녕하세요! 아리슬레나의 아리입니다.", color=discord.Colour.blue())

    for message in messages:
        embed.add_field(name="", value=message, inline=False)
    
    return embed

def parse_embeds(title:str, fields:list[dict], quantity:int=25) -> list[discord.Embed]:
    """
    embed를 여러 개 만들어서 반환합니다.
    ---
    title: embed의 제목
    quantity: 한 embed에 들어갈 field의 수 (기본값: 25)
    args' component = {
        "name" : ...,
        "value" : ...,
        "inline" : True / False
    }
    """
    embeds = []
    embed = discord.Embed(title=title, color=discord.Colour.blue())
    for field in fields:
        embed.add_field(**field)
        if len(embed.fields) == quantity:
            embeds.append(embed)
            embed = discord.Embed(title=title, color=discord.Colour.blue())
    embeds.append(embed)
    return embeds

def has_role(roles:list[discord.Role], role_name) -> bool:
    """
    roles에 role_name이 있는지 확인합니다.
    """
    for role in roles:
        if role.name == role_name:
            return True
    return False

def check_role(roles: list, correct_value: str):
    """
    유저 역할을 확인하고, correct_value에 반하면 오류를 출력하기\n
    correct_value에 합당하면 아무것도 하지 않음
    """
    
    if not correct_value in [role.name for role in roles]:
        if correct_value == "관리자":
            raise warning.NotAdmin()
        elif correct_value == "주인":
            raise warning.NotOwner()
        
def check_any_roles(roles: list, *correct_value):
    """
    유저 역할을 확인하고, correct_value에 반하면 오류를 출력하기\n
    correct_value에 합당하면 아무것도 하지 않음
    """
    
    if not any([role.name in correct_value for role in roles]):
        raise warning.NotAnyRole(correct_value)

def check_role_if_admin_mode(settings:jsonobj.Settings, roles:list):
    '''
    관리자 모드면 관리자 역할 체크, 아니면 아무것도 하지 않음
    ---------------------------
    return: 관리자 모드: True, 아니면 False
    '''
    try:
        if settings.admin_mode: check_role(roles, "관리자")
    except warning.Default:
        raise warning.Default("현재 관리자 모드 실행 중입니다! 정보, 목록, 열람 계열을 제외한 명령어는 한시적으로 관리자만 사용 가능합니다.")
    
def is_gaming(schedule:jsonobj.Schedule):
    '''
    게임 중인지 알려주는 함수
    gaming() 함수에 종속
    ---------------------------
    return: 게임 중: True, 아니면 False
    '''

    return True if schedule.state == 1 else False

def check_gaming(correct_value:bool):
    """
    게임 중인지 아닌지 확인하고, correct_value에 반하면 오류를 출력하기\n
    correct_value에 합당하면 아무것도 하지 않음
    """

    if is_gaming() != correct_value:
        if correct_value:
            # 게임 중이어야 하는데 게임 중이 아닐 때
            raise warning.NotGamingNow()
        else:
            # 게임 중이 아니어야 하는데 게임 중일 때
            raise warning.GamingNow()