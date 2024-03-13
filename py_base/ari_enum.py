"""
상태를 나타내는 모듈 (모든 상태가 한데 모여있음)
"""
from enum import IntEnum
import random

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

# TODO : 이 밑으로는 모두 바뀐 ArislenaEnum에 맞게 수정 필요
# local_name, emoji 추가

class HumanSex(ArislenaEnum):
    # 0: 남성, 1: 여성
    MALE = "남성", "♂"
    FEMALE = "여성", "♀"

class TerritorySafety(ArislenaEnum):
    # 회색, 흑색, 적색, 황색, 녹색
    # 회색 : 미확인
    # 흑, 적, 황, 녹 순으로 안전
    UNKNOWN = "미확인", "🔘"
    BLACK = "흑색", "⚫"
    RED = "적색", "🔴"
    YELLOW = "황색", "🟡"
    GREEN = "녹색", "🟢"

    @classmethod
    def max_value(cls):
        return cls.GREEN.value
    
    @classmethod
    def get_randomly(cls) -> "TerritorySafety":
        # p = list(cls._get_ratio_map().values())
        # a = list(range(1, len(p)+1))
        # p = [0.2, 0.8, 0.2]
        # a = [cls.BLACK, cls.RED, cls.YELLOW]
        # cls.BLACK, cls.RED, cls.YELLOW를 각각 1, 4, 1개씩 넣는다.
        
        return random.choice([cls.BLACK, cls.YELLOW, cls.RED, cls.RED, cls.RED, cls.RED])
        
class ResourceCategory(ArislenaEnum):
    UNSET = "미정", "❓"
    WATER = "물", "💧"
    FOOD = "식량", "🍞"
    FEED = "사료", "🌾"
    WOOD = "목재", "🌲"
    SOIL = "흙", "🏞️"
    STONE = "석재", "🥌"
    BUILDING_MATERIAL = "건축자재", "🧱"
    LIVESTOCK = "가축", "🐄"

class BuildingCategory(ArislenaEnum):
    UNSET = "미정", "❓"
    FRESH_WATER_SOURCE = "담수원", "🚰"
    HUNTING_GROUND = "수렵지", "🏹⛺"
    PASTURELAND = "목초지", "🐄⛺"
    FARMLAND = "농경지", "🌾⛺"
    WOOD_GATHERING_POST = "목재 채취장", "🌲🏭"
    EARTH_GATHERING_POST = "토석 채취장", "🏞️🏭"
    BUILDING_MATERIAL_FACTORY = "건축자재 공장", "🧱🏭"
    RECRUITING_CAMP = "모병소", "🛡️🏭"
    AUTOMATED_GATHERING_FACILITY = "자동 채취 시설", "🏭🤖"
    
    @classmethod
    def get_ramdom_base_building_category(cls) -> "BuildingCategory":
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
        rtn = [component for component in cls if component not in cls.get_basic_building_list() and component != cls.UNSET]
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

