"""
디스코드 명령어 실행 전 필요사항을 체크하는 함수 모음
모든 함수는 인자로 interaction: discord.Interaction을 받고, bool을 반환함
"""

import discord

from py_system._global import setting_by_guild

def is_admin(interaction:discord.Interaction) -> bool:
    """
    interaction.user가 관리자 역할을 가지고 있는지 확인합니다.
    """
    if (guild_id_key := str(interaction.user.guild.id)) in setting_by_guild.admin_role_id:
        if discord.utils.get(
                interaction.user.guild.roles, 
                id=setting_by_guild.admin_role_id[guild_id_key]
            ):
            return True

    return False

def is_user(interaction:discord.Interaction) -> bool:
    """
    interaction.user가 유저 역할을 가지고 있는지 확인합니다.
    """
    if (guild_id_key := str(interaction.user.guild.id)) in setting_by_guild.user_role_id:
        if discord.utils.get(
                interaction.user.guild.roles, 
                id=setting_by_guild.user_role_id[guild_id_key]
            ):
            return True
    return False

def user_exists(interaction:discord.Interaction) -> bool:
    """
    interaction.user가 아리슬레나에 등록되어 있는지 확인합니다.
    """
    
    if interaction.client.guild_database[str(interaction.guild_id)].is_exist("user", discord_ID = interaction.user.id):
        return True
    return False

# def check_role(roles: list, correct_value: str):
#     """
#     유저 역할을 확인하고, correct_value에 반하면 오류를 출력하기\n
#     correct_value에 합당하면 아무것도 하지 않음
#     """
    
#     if not correct_value in [role.name for role in roles]:
#         if correct_value == "관리자":
#             raise warnings.NotAdmin()
#         elif correct_value == "주인":
#             raise warnings.NotOwner()
        
# def check_any_roles(roles: list, *correct_value):
#     """
#     유저 역할을 확인하고, correct_value에 반하면 오류를 출력하기\n
#     correct_value에 합당하면 아무것도 하지 않음
#     """
    
#     if not any([role.name in correct_value for role in roles]):
#         raise warnings.NotAnyRole(correct_value)

# def check_role_if_admin_mode(settings, roles:list):
#     '''
#     관리자 모드면 관리자 역할 체크, 아니면 아무것도 하지 않음
#     ---------------------------
#     return: 관리자 모드: True, 아니면 False
#     '''
#     try:
#         if settings.admin_mode: check_role(roles, "관리자")
#     except warnings.Default:
#         raise warnings.Default("현재 관리자 모드 실행 중입니다! 정보, 목록, 열람 계열을 제외한 명령어는 한시적으로 관리자만 사용 가능합니다.")
    
# def is_gaming(schedule:jsonobj.Schedule):
#     '''
#     게임 중인지 알려주는 함수
#     gaming() 함수에 종속
#     ---------------------------
#     return: 게임 중: True, 아니면 False
#     '''

#     return True if schedule.state == 1 else False

# def check_gaming(correct_value:bool):
#     """
#     게임 중인지 아닌지 확인하고, correct_value에 반하면 오류를 출력하기\n
#     correct_value에 합당하면 아무것도 하지 않음
#     """

#     if is_gaming() != correct_value:
#         if correct_value:
#             # 게임 중이어야 하는데 게임 중이 아닐 때
#             raise warnings.NotGamingNow()
#         else:
#             # 게임 중이 아니어야 하는데 게임 중일 때
#             raise warnings.GamingNow()