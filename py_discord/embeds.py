from discord import Embed, Colour, utils
from enum import IntEnum

from py_base import abstract
from py_system import tableobj

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
def register(user:tableobj.User):
    """
    유저 등록
    """
    embed = Embed(title="환영합니다!", description="다음 정보가 저장되었습니다.", color=Colour.green())
    embed.add_field(name="디스코드 아이디", value=user.discord_id)
    embed.add_field(name="유저네임", value=user.discord_name)
    embed.add_field(name="등록일", value=user.register_date)
    return embed

def table_info_text_list(table_obj:abstract.TableObject) -> list[str]:
    """
    테이블 객체의 정보를 텍스트로 반환합니다.
    """
    texts = []
    for key, value in table_obj.kr_dict.items():
        if isinstance(value, IntEnum):
            value = f"**{value.name}** ({value.value})"
        else:
            value = f"**{value}**"
        texts.append(f"- {key} : {value}")
    return texts

# 각종 정보 열람 시 테이블에 있는 데이터를 자동으로 반환하는 함수
def table_info(embed:Embed, table_obj:abstract.TableObject):

    embed.add_field(name="기본 정보", value="\n".join(table_info_text_list(table_obj)))
    
    return embed

# 자신이 세운 세력 정보 열람
def faction_info(title, color, ):
    """
    엠베드 제목 : (세력명) 정보\n
    엠베드 색깔 : 세력 데이터의 main_color\n
    """
    embed = Embed(title=title, color=color)

