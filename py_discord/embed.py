from discord import Embed, Colour

from py_system import tableobj

# /유저 등록
def register(user:tableobj.User):
    """
    유저 등록
    """
    embed = Embed(title="환영합니다!", description="다음 정보가 저장되었습니다.", color=Colour.green())
    embed.add_field(name="디스코드 아이디", value=user.discord_ID)
    embed.add_field(name="유저네임", value=user.discord_name)
    embed.add_field(name="등록일", value=user.register_date)
    return embed


# 자신이 세운 세력 정보 열람
def faction_info(title, color, ):
    """
    엠베드 제목 : (세력명) 정보\n
    엠베드 색깔 : 세력 데이터의 main_color\n
    """
    embed = Embed(title=title, color=color)

