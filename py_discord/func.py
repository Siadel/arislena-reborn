from discord.app_commands import Choice

from py_base.ari_enum import BuildingCategory
from py_system._global import name_regex, translate
from py_discord.warnings import NameContainsSpecialCharacter



def check_special_character_and_raise(name:str):
    """
    이름에 특수문자가 포함되어 있는지 확인하고, 포함되어 있다면 오류를 출력합니다.
    """
    if not name_regex.search(name):
        raise NameContainsSpecialCharacter()
    
def get_building_category_choices() -> list[Choice[int]]:
    """
    건물 카테고리 선택지를 반환합니다.
    
    note : Choice 객체의 type annotation은 value의 type을 기준으로 해야 합니다.
    """
    return [
        Choice(
            name=translate.get_from_map("ari_enum", category.name, default=category.name),
            value=category.value
        ) for category in BuildingCategory.get_advanced_building_list()
    ]