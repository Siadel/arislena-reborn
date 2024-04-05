from discord import Embed, Colour, utils
from enum import Enum

from py_base.abstract import ArislenaEnum
from py_system.abstract import TableObject
from py_system.tableobj import User
from py_system._global import translate

def embed_for_user(*messages) -> Embed:
    """
    유저 DM으로 보낼 embed 생성
    """

    embed = Embed(title="안녕하세요! 아리슬레나의 아리입니다.", color=Colour.blue())

    for message in messages:
        embed.add_field(name="", value=message, inline=False)
    
    return embed

def parse_embeds(title:str, fields:list[dict], quantity:int=25) -> list[Embed]:
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
    embed = Embed(title=title, color=Colour.blue())
    for field in fields:
        embed.add_field(**field)
        if len(embed.fields) == quantity:
            embeds.append(embed)
            embed = Embed(title=title, color=Colour.blue())
    embeds.append(embed)
    return embeds

# /유저 등록
def register(user:User):
    """
    유저 등록
    """
    embed = Embed(title="환영합니다!", description="다음 정보가 저장되었습니다.", color=Colour.green())
    embed.add_field(name="디스코드 아이디", value=user.discord_id)
    embed.add_field(name="유저네임", value=user.discord_name)
    embed.add_field(name="등록일", value=user.register_date)
    return embed

def add_basic_table_info(embed:Embed, table_obj:TableObject):
    """
    열람 계열 명령어 실행 시 사용자에게 출력할 TableObject의 기본 정보를 embed에 추가합니다.
    """

    embed.add_field(name="기본 정보", value=table_obj.to_discord_text(translate))
    
    return embed


