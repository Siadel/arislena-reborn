from py_system._global import name_regex
from py_discord.warnings import NameContainsSpecialCharacter

def check_special_character_and_raise(name:str):
    """
    이름에 특수문자가 포함되어 있는지 확인하고, 포함되어 있다면 오류를 출력합니다.
    """
    if not name_regex.search(name):
        raise NameContainsSpecialCharacter()