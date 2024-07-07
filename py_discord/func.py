from discord.app_commands import Choice

from py_base.ari_enum import BuildingCategory, Availability
from py_base.dbmanager import DatabaseManager
from py_base.utility import name_regex
from py_base.yamlobj import Detail
from py_system.systemobj import Crew
from py_system.tableobj import WorkerDescription, Faction, Territory, Building
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

def make_and_push_new_crew_package(database: DatabaseManager, new_crew: Crew, file:Detail) -> None:
    """
    새로운 Crew 객체를 생성할 때, CrewPersonality 객체도 같이 생성하고, 데이터베이스에 추가합니다.
    """
    if new_crew.database is None: new_crew.set_database(database)
    new_crew.availability = Availability.STANDBY
    new_crew.push()
    crew_personality = WorkerDescription.new(database.cursor.lastrowid, file)
    crew_personality.set_database(new_crew.database)
    crew_personality.push()

def make_and_push_new_faction(database: DatabaseManager, new_faction: Faction):
    """
    새로운 Faction 객체를 데이터베이스에 추가하고, 반환합니다.
    """
    
    new_faction.set_database(database)
    new_faction.push()
    
    database.connection.commit()
    
    new_faction = Faction.from_database(database, user_id=new_faction.user_id)
    
    return new_faction

def add_new_territory_set(database: DatabaseManager, faction: Faction):
    """
    새로운 Territory 객체(담수원, 수렵지, 목초지, 채집지)를 생성하고, 데이터베이스에 추가합니다.
    """
    for b_cat in BuildingCategory.get_basic_building_list():
        t = Territory(faction_id=faction.id)
        t.name = f"{faction.name}의 {b_cat.local_name}"
        t.set_safety_by_random()
        t.set_database(database)
        t.push()
        # 건물을 만들기 위해서는 id가 정해진 후에 생성해야 함
        t = Territory.from_database(database, id=database.cursor.lastrowid)
        b = Building(
            faction_id=faction.id,
            territory_id=t.id,
            category=b_cat,
            name=b_cat.local_name
        ).set_database(database)
        b.push()

