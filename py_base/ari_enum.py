"""
상태를 나타내는 모듈 (모든 상태가 한데 모여있음)
"""
from enum import IntEnum, auto
from numpy import random

from py_base.abstract import ArislenaEnum

def get_enum(enum_class_name, value:int|None) -> IntEnum:
    """
    enum을 반환함
    """
    if value is None: raise ValueError("enum의 값이 None입니다. 데이터에서 값을 확인해주세요.")
    return globals()[enum_class_name](value)


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

class HumanSex(ArislenaEnum):
    # 0: 남성, 1: 여성
    MALE = 0
    FEMALE = 1

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
    def get_ramdomly_base_building(cls) -> "BuildingCategory":
        return random.choice([cls.FRESH_WATER_SOURCE, cls.HUNTING_GROUND, cls.PASTURELAND])
    
    @classmethod
    def get_basic_building_list(cls) -> list["BuildingCategory"]:
        return [
            cls.FRESH_WATER_SOURCE,
            cls.HUNTING_GROUND,
            cls.PASTURELAND
        ]
    
    @classmethod
    def get_advanced_building_list(cls) -> list["BuildingCategory"]:
        rtn = [component for component in cls if component not in cls.get_basic_building_list()]
        rtn.remove(cls.UNSET)
        return rtn

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

