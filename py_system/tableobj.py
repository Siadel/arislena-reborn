"""
Sql과 연동되는 데이터 클래스들
"""
from dataclasses import dataclass

from py_base import ari_enum
from py_base.datatype import ExtInt
from py_system.abstract import TableObject

def convert_to_tableobj(table_name:str, data:list) -> TableObject:
    """
    sql 테이블 데이터에서 불러온 데이터를 이곳에 구현된 클래스로 변환하는 함수\n
    자료형이 ExtInt인 경우, ExtInt에 데이터의 int값을 더해서 반환함 (기본적으로 ExtInt는 0으로 초기화됨)
    주의: 이 함수는 **반드시** py_system.tableobj 모듈에 있어야 함
    """
    # table_name의 첫 글자를 대문자로 바꿔서 클래스 이름으로 사용
    table_name = table_name[0].upper() + table_name[1:]
    tableobj:TableObject = globals()[table_name]()
    for key, value in zip(tableobj.items.keys(), data):

        if "ExtInt" in str(tableobj.__annotations__[key]):
            tableobj.__setattr__(key, tableobj.__getattribute__(key) + value)
        else:
            tableobj.__setattr__(key, value)
        # if not isinstance(value, int):
        #     tableobj.__setattr__(key, value)
        # else:
        #     if "ExtInt" in str(tableobj.__annotations__[key]):
        #         tableobj.__setattr__(key, tableobj.__getattribute__(key) + value)
        #     else:
        #         tableobj.__setattr__(key, value)
    return tableobj

"""
!! ---------------------- 주의 ---------------------- !!

abstract methods: kr_list
필수로 작성해야 할 메소드: __post_init__ 
"""

"""
액티브 데이터
"""
@dataclass(slots=True)
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
    
    def __post_init__(self):
        self.display_main = "discord_name"
        

@dataclass(slots=True)
class Faction(TableObject):
    ID: int = None
    user_ID: int = None
    name: str = None
    level: int = 0

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "유저 아이디",
            "세력명",
            "레벨"
        ]
    
    def __post_init__(self):
        self.display_main = "name"
        

@dataclass(slots=True)
class FactionHierarchyNode(TableObject):
    ID: int = None
    higher: int = None
    lower: int = None

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "상위 세력",
            "하위 세력"
        ]
    
    def __post_init__(self):
        self.display_main = "higher"
        

@dataclass(slots=True)
class Population(TableObject):
    ID: int = None
    faction_ID: int = None
    name: str = None
    labor:int = 1
    food_consumption:int = 1
    water_consumption:int = 1
    is_laboring:int = ari_enum.YesNo.NO.value

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "세력 아이디",
            "이름",
            "노동력",
            "식량 소비",
            "물 소비",
            "노동 중"
        ]
    
    def __post_init__(self):
        self.display_main = "name"
        

@dataclass(slots=True)
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
    
    def __post_init__(self):
        self.display_main = "ID"
        

@dataclass(slots=True)
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
    
    def __post_init__(self):
        self.display_main = "ID"
        

@dataclass(slots=True)
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
    
    def __post_init__(self):
        self.display_main = "ID"
        

@dataclass(slots=True)
class Territory(TableObject):
    """
    safety: 안전도. 회색, 흑색, 적색, 황색, 녹색으로 분류. ari_enum.TerritorySafety 참고
        회색 : 미확인 |
        흑, 적, 황, 녹 순으로 안전
    """
    ID: int = None
    faction_ID: int = None
    name: str = None
    space_limit: int = 1
    safety: int = 0

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "세력 아이디",
            "이름",
            "공간 제한",
            "안정도"
        ]
    
    def __post_init__(self):
        self.display_main = "name"
        

@dataclass(slots=True)
class Building(TableObject):
    ID: int = None
    territory_ID: int = None
    discriminator: str = None
    name: str = None

    @property
    def kr_list(self) -> list[str]:
        return [
            "아이디",
            "영토 아이디",
            "구분",
            "이름"
        ]
    
    def __post_init__(self):
        self.display_main = "name"
        