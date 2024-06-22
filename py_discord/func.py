from discord.app_commands import Choice

from py_base.ari_enum import BuildingCategory
from py_base.dbmanager import DatabaseManager
from py_system.systemobj import Crew
from py_system.tableobj import WorkerDescription
from py_base.utility import name_regex
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
            name=category.local_name,
            value=category.value
        ) for category in BuildingCategory.get_advanced_building_list()
    ]

def make_and_push_new_crew_package(database: DatabaseManager, new_crew: Crew) -> None:
    """
    새로운 Crew 객체를 생성할 때, CrewPersonality 객체도 같이 생성하고, 데이터베이스에 추가합니다.
    """
    if new_crew.database is None: new_crew.set_database(database)
    new_crew.push()
    crew_personality = WorkerDescription.new(database.cursor.lastrowid)
    crew_personality.set_database(new_crew.database)
    crew_personality.push()