from discord.app_commands import Choice

from py_base.ari_enum import FacilityCategory, Availability
from py_base.dbmanager import DatabaseManager
from py_base.utility import name_regex
from py_base.yamlobj import Detail
from py_system.tableobj import Facility
from py_system.worker import Crew
from py_system.tableobj import WorkerDescription, Faction, Territory
from py_discord.warnings import NameContainsSpecialCharacter




def check_special_character_and_raise(name:str):
    """
    이름에 특수문자가 포함되어 있는지 확인하고, 포함되어 있다면 오류를 출력합니다.
    """
    if not name_regex.search(name):
        raise NameContainsSpecialCharacter()
    
def get_facility_category_choices() -> list[Choice[int]]:
    """
    시설 카테고리 선택지를 반환합니다.
    
    note : Choice 객체의 type annotation은 value의 type을 기준으로 해야 합니다.
    """
    return [
        Choice(
            name=category.local_name,
            value=category.value
        ) for category in FacilityCategory.get_advanced_facility_list()
    ]

def make_and_push_new_crew_package(database: DatabaseManager, new_crew: Crew, detail:Detail) -> None:
    """
    새로운 Crew 객체를 생성할 때, CrewPersonality 객체도 같이 생성하고, 데이터베이스에 추가합니다.
    """
    if new_crew.database is None: new_crew.set_database(database)
    new_crew.availability = Availability.STANDBY
    new_crew.push()
    crew_personality = WorkerDescription.new(database.cursor.lastrowid, detail)
    crew_personality.set_database(new_crew.database)
    crew_personality.push()

def make_and_push_new_faction(database: DatabaseManager, new_faction: Faction):
    """
    새로운 Faction 객체를 데이터베이스에 추가하고, 반환합니다.
    """
    user_id = new_faction.user_id
    
    new_faction.set_database(database)
    new_faction.push()
    
    database.connection.commit()
    
    del new_faction
    new_faction = Faction.from_database(database, user_id=user_id)
    
    return new_faction

