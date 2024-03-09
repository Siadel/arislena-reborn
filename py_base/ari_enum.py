"""
상태를 나타내는 모듈 (모든 상태가 한데 모여있음)
"""
from enum import IntEnum, auto
from numpy import random

def get_enum(enum_class_name, value:int|None) -> IntEnum:
    """
    enum을 반환함
    """
    if value is None: raise ValueError("enum의 값이 None입니다. 데이터에서 값을 확인해주세요.")
    return globals()[enum_class_name](value)

class ArislenaEnum(IntEnum):
    """
    Arislena에서 사용하는 Enum의 기본 클래스
    """
    def __str__(self) -> str:
        return self.name
    
    def __int__(self) -> int:
        return self.value
    
    def __repr__(self) -> str:
        return super().__repr__()
    
    @classmethod
    def get_kr_list(cls) -> list[str]:
        raise NotImplementedError("이 메소드는 반드시 구현되어야 합니다.")
    
    def to_kr(self) -> str:
        return self.get_kr_list()[self.value]

# 스케줄 상태
class ScheduleState(IntEnum):
    # 0: 시작 대기, 1: 게임 중, 2: 중단, 3: 종료
    WAITING = 0
    ONGOING = 1
    PAUSED = 2
    ENDED = 3

# 범용 예, 아니요
class YesNo(IntEnum):
    YES = 1
    NO = 0

# 인구 분류
class HumanClass(ArislenaEnum):
    # 0: 일반인력, 1: 고급인력
    COMMON = 0
    ADVANCED = 1
    
    @classmethod
    def get_kr_list(cls) -> list[str]:
        return ["일반인력", "고급인력"]

class HumanSex(ArislenaEnum):
    # 0: 남성, 1: 여성
    MALE = 0
    FEMALE = 1
    
    @classmethod
    def get_kr_list(cls) -> list[str]:
        return ["남성", "여성"]

class TerritorySafety(ArislenaEnum):
    # 회색, 흑색, 적색, 황색, 녹색
    # 회색 : 미확인
    # 흑, 적, 황, 녹 순으로 안전
    UNKNOWN = 0
    BLACK = 1
    RED = 2
    YELLOW = 3
    GREEN = 4
    
    @classmethod
    def get_kr_list(cls) -> list[str]:
        return ["회색", "흑색", "적색", "황색", "녹색"]

    @classmethod
    def max_value():
        return max(TerritorySafety.__members__.values()).value
    
    @classmethod
    def get_randomly(cls) -> "TerritorySafety":
        return cls(random.choice(list(range(1, 4)), p=list(cls._get_ratio_map().values())))
    
    @staticmethod
    def _get_ratio_map() -> dict["TerritorySafety", float]:
        return {
            TerritorySafety.BLACK : 0.2,
            TerritorySafety.RED : 0.6,
            TerritorySafety.YELLOW : 0.2,
        }
        
class ResourceCategory(ArislenaEnum):
    UNSET = 0
    WATER = auto()
    FOOD = auto()
    FEED = auto()
    WOOD = auto()
    SOIL = auto()
    STONE = auto()
    BUILDING_MATERIAL = auto()
    LIVESTOCK = auto()
    
    @classmethod
    def get_kr_list(cls) -> list[str]:
        return ["미지정", "물", "식량", "사료", "목재", "흙", "석재", "건축자재", "가축"]

class BuildingCategory(ArislenaEnum):
    UNSET = 0
    FRESH_WATER_SOURCE = auto()
    HUNTING_GROUND = auto()
    PASTURELAND = auto()
    FARMLAND = auto()
    WOOD_GATHERING_POST = auto()
    EARTH_GATHERING_POST = auto()
    BUILDING_MATERIAL_FACTORY = auto()
    RECRUITING_CAMP = auto()
    AUTOMATED_GATHERING_FACILITY = auto()
    
    @classmethod
    def get_kr_list(cls) -> list[str]:
        return ["미지정", "담수원", "수렵지", "목초지", "농경지", "목재 채취장", "토석 채취장", "건축자재 공장", "모병소", "자동 채취 시설"]
    
    @classmethod
    def get_ramdomly_base_building(cls) -> "BuildingCategory":
        return random.choice([cls.FRESH_WATER_SOURCE, cls.HUNTING_GROUND, cls.PASTURELAND])
    

# # 부대 상태
# class Troop(IntEnum):
#     IDLE = 0
#     ALERT = 1
#     FORTIFYING = 2
#     MOVING = 3
# # 블럭 상태
# class Block(IntEnum):
#     SAFE = 0
#     CRISIS = 1
#     CONQUERED = 2
# # 건물 상태
# class Building(IntEnum):
#     ONGOING_CONSTRUCTION = 0
#     COMPLETED = 1
#     PILLAGED = 2
# # 기술 상태
# class Technology(IntEnum):
#     ONGOING_RESEARCH = 0
#     COMPLETED = 1
#     SABOTAGED = 2

