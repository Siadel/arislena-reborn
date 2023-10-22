"""
디스코드 명령어 실행 전 필요사항을 체크하는 함수 모음
모든 함수는 인자로 interaction: discord.Interaction을 받고, bool을 반환함
"""

import discord

def is_admin(interaction: discord.Interaction) -> bool:
    """
    interaction.user가 관리자 역할을 가지고 있는지 확인합니다.
    """
    for role in interaction.user.roles:
        if role.name == "관리자":
            return True
    return False

def is_owner(interaction: discord.Interaction) -> bool:
    """
    interaction.user가 주인 역할을 가지고 있는지 확인합니다.
    """
    for role in interaction.user.roles:
        if role.name == "주인":
            return True
    return False