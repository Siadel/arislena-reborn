"""
Sql과 연동되는 데이터 클래스들
"""
from abc import ABCMeta
from dataclasses import dataclass
from py_base import enums
from py_base.datatype import ExtInt
from copy import deepcopy

class TableObject(metaclass=ABCMeta):
    """
    테이블 오브젝트 (db 파일의 table로 저장되는 녀석들)
    """
    def __iter__(self):
        rtn = list(self.__dict__.values())
        rtn.pop(0) # ID 제거
        return iter(rtn)

    @classmethod
    def get_table_name(cls):
        """
        테이블명은 항상 소문자로만 구성되어 있음
        """
        return cls.__name__.lower()

    @classmethod
    def get_column_set(cls):
        """
        테이블의 컬럼명을 집합으로 반환
        """
        return set(cls.__annotations__.keys())

    def get_keys_string(self) -> str:
        """
        sql문에서 컬럼명을 채우기 위한 문자열 반환\n
        ID는 제외함
        """
        keys = list(self.__dict__.keys())
        keys.remove("ID")
        return ", ".join(keys)

    def get_values_string(self) -> str:
        """
        sql문에서 컬럼값을 채우기 위한 문자열 반환\n
        ID는 제외함
        """
        values = list(self.__dict__.values())
        values.pop(0)
        return ", ".join([f"'{value}'" if isinstance(value, str) else str(value) for value in values])
    
    def get_wildcard_string(self) -> str:
        """
        sql문에서 ?를 채우기 위한 문자열 반환
        """
        return ", ".join(["?" for i in range(len(self.__dict__) - 1)])
    
    @classmethod
    def get_create_table_string(cls) -> str:
        """
        sql문에서 테이블 생성을 위한 문자열 반환
        """
        sql = f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} ("
        for key, value in cls.__annotations__.items():
            if key == "ID":
                sql += f"{key} INTEGER PRIMARY KEY AUTOINCREMENT, "
            else:
                if "str" in str(value).lower():
                    sql += f"{key} TEXT, "
                elif "int" in str(value).lower():
                    sql += f"{key} INTEGER, "
                elif "float" in str(value).lower():
                    sql += f"{key} REAL, "
                else:
                    raise Exception("데이터 타입을 알 수 없습니다.")
        sql = sql[:-2] + ")"
        return sql

def convert_to_tableobj(table_name:str, data:list) -> TableObject:
    """
    sql 테이블 데이터에서 불러온 데이터를 이곳에 구현된 클래스로 변환하는 함수\n
    자료형이 ExtInt인 경우, ExtInt에 데이터의 int값을 더해서 반환함 (기본적으로 ExtInt는 0으로 초기화됨)
    """
    tableobj = globals()[table_name.capitalize()]()
    for key, value in zip(tableobj.__dict__.keys(), data):
        if not isinstance(value, int):
            tableobj.__setattr__(key, value)
        else:
            if "ExtInt" in str(tableobj.__annotations__[key]):
                tableobj.__setattr__(key, tableobj.__getattribute__(key) + value)
            else:
                tableobj.__setattr__(key, value)
    return tableobj

"""
액티브 데이터
"""
@dataclass
class User(TableObject):
    ID: int = None
    discord_id: int = None
    discord_name: str = None
    register_date: str = None

@dataclass
class Faction(TableObject):
    ID: int = None
    user_ID: int = None
    name: str = None
    scale: ExtInt = ExtInt(0, min_value = 0)
    finance: ExtInt = ExtInt(0, min_value = 0)
    manpower: ExtInt = ExtInt(0, min_value = 0)
    motive_power: ExtInt = ExtInt(0, min_value = 0)
    stability: ExtInt = ExtInt(0, min_value = -20, max_value = 100)

    @classmethod
    def get_translate(cls, *attribute_name):
        data = {
            "ID": "아이디",
            "user_ID": "유저 아이디",
            "name": "집단명",
            "scale": "규모",
            "finance": "자산",
            "manpower": "인력",
            "motive_power": "동력",
            "stability": "안정도"
        }
        if len(attribute_name) == 0:
            return data
        else:
            clipped_data = {}
            for name in attribute_name:
                clipped_data[name] = deepcopy(data[name])
            return clipped_data

@dataclass
class Faction_data(TableObject):
    ID: int = None
    faction_ID: int = None
    main_color: int = 3447003
    sub_color: int = None
    spicies: str = None
    location: str = None
    philosophy: str = None
    favor: str = None
    taboo: str = None
    prolog: str = None
    present: str = None

@dataclass
class Knowledge(TableObject):
    ID: int = None
    faction_ID: int = None
    war: ExtInt = ExtInt(0, min_value = 0)
    argiculture: ExtInt = ExtInt(0, min_value = 0)
    industry: ExtInt = ExtInt(0, min_value = 0)
    governance: ExtInt = ExtInt(0, min_value = 0)
    diplomacy: ExtInt = ExtInt(0, min_value = 0)



# @dataclass
# class Block(TableObject):
#     ID: int
#     nation_ID : int
#     name: str
#     freshwater: int = 0
#     food: int = 0
#     material: int = 0
#     luxury: int = 0
#     status: int = enums.Block.SAFE

# @dataclass
# class Terrain(TableObject):
#     block_ID: int
#     defense: int
#     accessability: int

# @dataclass
# class Productivity(TableObject):
#     block_ID: int
#     freshwater: int
#     food: int
#     material: int
#     luxury: int

# @dataclass
# class Industry(TableObject):
#     block_ID: int
#     freshwater: int = 0
#     food: int = 0
#     material: int = 0
#     luxury: int = 0

# @dataclass
# class Troop(TableObject):
#     ID: int
#     nation_ID: int # 소속 나라
#     block_ID: int # 위치한 블럭
#     name: str
#     scale: int = 0
#     royalty: int = 0
#     # 군사 아이템
#     elite: int = 0
#     special: int = 0
#     general: int = 0
#     spear: int = 0
#     chariot: int = 0
#     stored_material: int = 0
#     siege_equipment: int = 0
#     # 기타 정보
#     status: int = enums.Troop.IDLE
#     attack_chance: int = 1 # 충전식, 0이 되면 공격 불가
#     move_to: int = None

# @dataclass
# class Nation(TableObject):
#     ID: int
#     user_ID: int
#     name: str
#     surplus_population: int = 20
#     fund: int = 50
#     settler: int = 0
#     cement: int = 0
#     supply: int = 0
#     sample: int = 0
#     immune: int = 0
#     royalty: int = 50
#     race: str = "인간"
#     fate: str = "자유인"
#     npc: int = 0
#     dev: int = 0

# @dataclass
# class Building(TableObject):
#     ID: int
#     block_ID: int
#     building_ID: int
#     status: int = enums.Building.ONGOING_CONSTRUCTION

# @dataclass
# class Technology(TableObject):
#     ID: int
#     nation_ID: int
#     technology_ID: int
#     status: int = enums.Technology.ONGOING_RESEARCH

# @dataclass
# class Diplomacy(TableObject):
#     category: str
#     from_nation_ID: int # 나라 ID
#     to_nation_ID: int # 나라 ID
#     expire: int

# @dataclass
# class Pending(TableObject):
#     ID: int
#     category: str  # 명령어 종류 (한국어)
#     mode: str  # active, passive
#     start: int  # 이 데이터가 만들어진 턴
#     execute: int  # 이 데이터가 실행되거나(active) 끝나는(passive) 턴
#     execute_code: str  # 실행 코드

# @dataclass
# class Extra(TableObject):
#     ID: int
#     owner_ID: int
#     nation_name: str
#     leader: str = None
#     religion: str = None
#     ethos: str = None
#     concern: str = None
#     foundation_story: str = None
#     extra: str = None
