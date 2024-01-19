"""
Sql과 연동되는 데이터 클래스들
"""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from py_base import ari_enum
from py_base.datatype import ExtInt
from py_system.abstract import TableObject

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
    discord_ID: int = None
    discord_name: str = None
    register_date: str = None

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "디스코드 아이디",
            "디스코드 이름",
            "가입일"
        ]
    

@dataclass
class User_setting(TableObject):
    ID: int = None
    discord_ID: int = None
    embed_color: int = 3447003

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "유저 아이디",
            "임베드 색상"
        ]

@dataclass
class Faction(TableObject):
    ID: int = None
    user_ID: int = None
    name: str = None

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "유저 아이디",
            "세력명"
        ]

@dataclass
class Population(TableObject):
    ID: int = None
    faction_ID: int = None
    classification:int = ari_enum.HumanClass.COMMON.value
    labor:int = 1
    food_consumption:int = 1
    water_consumption:int = 1
    is_laboring:int = ari_enum.YesNo.NO.value

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "세력 아이디",
            "분류",
            "노동력",
            "식량 소비",
            "물 소비",
            "노동 중"
        ]

@dataclass
class Livestock(TableObject):
    ID: int = None
    faction_ID: int = None
    labor:int = 1
    food_consumption:int = 1
    water_consumption:int = 1
    is_laboring:int = ari_enum.YesNo.NO.value

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "세력 아이디",
            "노동력",
            "식량 소비",
            "물 소비",
            "노동 중"
        ]

@dataclass
class Resource(TableObject):
    ID: int = None
    faction_ID: int = None
    water: ExtInt = ExtInt(0, min_value = 0)
    food: ExtInt = ExtInt(0, min_value = 0)
    feed: ExtInt = ExtInt(0, min_value = 0)
    wood: ExtInt = ExtInt(0, min_value = 0)
    soil: ExtInt = ExtInt(0, min_value = 0)
    building_material: ExtInt = ExtInt(0, min_value = 0)

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "세력 아이디",
            "물",
            "식량",
            "사료",
            "목재",
            "흙",
            "건축자재"
        ]

@dataclass
class ResourceStorage(TableObject):
    ID: int = None
    faction_ID: int = None
    # Resource 테이블에 있는 자원들
    # 초기값은 20
    water: ExtInt = ExtInt(20, min_value = 0)
    food: ExtInt = ExtInt(20, min_value = 0)
    feed: ExtInt = ExtInt(20, min_value = 0)
    wood: ExtInt = ExtInt(20, min_value = 0)
    soil: ExtInt = ExtInt(20, min_value = 0)
    building_material: ExtInt = ExtInt(20, min_value = 0)

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "세력 아이디",
            "물",
            "식량",
            "사료",
            "목재",
            "흙",
            "건축자재"
        ]

# @dataclass
# class Faction_data(TableObject):
#     ID: int = None
#     faction_ID: int = None
#     spicies: str = None
#     location: str = None
#     philosophy: str = None
#     favor: str = None
#     taboo: str = None
#     prolog: str = None
#     present: str = None

#     @property
#     def kr_list(self) -> list[str]:
#         return [
#             "아이디",
#             "세력 아이디",
#             "종족",
#             "활동 지역",
#             "철학",
#             "선호하는 것",
#             "금지하는 것",
#             "역사",
#             "현재"
#         ]

# @dataclass
# class Knowledge(TableObject):
#     ID: int = None
#     faction_ID: int = None
#     war: ExtInt = ExtInt(0, min_value = 0)
#     argiculture: ExtInt = ExtInt(0, min_value = 0)
#     industry: ExtInt = ExtInt(0, min_value = 0)
#     governance: ExtInt = ExtInt(0, min_value = 0)
#     diplomacy: ExtInt = ExtInt(0, min_value = 0)

#     @property
#     def kr_list(self) -> list[str]:
#         return [
#             "아이디",
#             "세력 아이디",
#             "전쟁 지식",
#             "농업 지식",
#             "산업 지식",
#             "통치 지식",
#             "외교 지식"
#         ]


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
