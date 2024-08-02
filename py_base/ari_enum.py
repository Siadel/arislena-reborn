"""
상태를 나타내는 모듈 (모든 상태가 한데 모여있음)
"""
from enum import IntEnum, Enum
import random
import numpy.random as npr

from py_base.abstract import ArislenaEnum, DetailEnum

def get_intenum(enum_class_name: str, value:int|None) -> IntEnum:
    """
    enum을 반환함
    """
    if value is None: raise ValueError("enum의 값이 None입니다. 데이터에서 값을 확인해주세요.")
    return globals()[enum_class_name](value)

def get_enum(enum_class_name: str, value:str|None) -> Enum:
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

# TODO : 이 밑으로는 모두 바뀐 ArislenaEnum에 맞게 수정 필요
# local_name, emoji 추가

class Language(ArislenaEnum):
    # 0: 한국어, 1: 영어
    KOREAN = "한국어", "🇰🇷"
    ENGLISH = "English", "🇺🇸"

class BiologicalSex(ArislenaEnum):
    # 0: 남성, 1: 여성
    UNSET = "미정", "❓", -1
    MALE = "남성", "♂"
    FEMALE = "여성", "♀"
    
    @classmethod
    def get_random(cls):
        
        return cls(npr.choice(2, 1, p=[0.9, 0.1])+1)

class Availability(ArislenaEnum):
    UNAVAILABLE = "배치 불가", "❌"
    HEALING = "치료 중", "🩹"
    LABORING = "노동 중 (배치됨)", "🛠️", 1
    STANDBY = "대기 중", "✅", 1
    
    @classmethod
    def get_availables(cls):
        return [cls.LABORING, cls.STANDBY]
    
    def is_available(self) -> bool:
        return self in self.__class__.get_availables()

class TerritorySafety(ArislenaEnum):
    # 회색, 흑색, 적색, 황색, 녹색
    # 회색 : 미확인
    # 흑, 적, 황, 녹 순으로 안전
    UNKNOWN = "미확인", "🔘", -1
    BLACK = "흑색", "⚫"
    RED = "적색", "🔴", 1
    YELLOW = "황색", "🟡", 1
    GREEN = "녹색", "🟢", 1

    @classmethod
    def get_max_safety(cls):
        return cls.GREEN
    
    @classmethod
    def get_randomly(cls):
        # 황 80%, 적 20%
        
        return cls(npr.choice(2, 1, p=[0.8, 0.2])+2)
        
class ResourceCategory(ArislenaEnum):
    UNSET = "미정", "❓", -1
    WATER = "물", "💧"
    FOOD = "식량", "🍞"
    FEED = "사료", "🌾"
    WOOD = "목재", ":wood:"
    SOIL = "흙", "🟫"
    STONE = "석재", ":rock:"
    BUILDING_MATERIAL = "건축자재", "🧱"
    HERB = "약재", "🌿"
    
    @classmethod
    def to_list(cls) -> list["ResourceCategory"]:
        return [component for component in cls if component.value != cls.UNSET.value]

class TerritoryCategory(ArislenaEnum):
    UNSET = "미정", "❓", -1
    
    
    @classmethod
    def get_randomly(cls):
        return random.choice([comp for comp in cls if comp.level == 0])

class FacilityCategory(ArislenaEnum):
    UNSET = "미정", "❓", -1
    FRESH_WATER_SOURCE = "담수원", "🚰"
    HUNTING_GROUND = "수렵지", "🏹"
    GATHERING_POST = "채집지", "🌾"
    PASTURELAND = "목초지", "🐄"
    FARMLAND = "농경지", "🌾⛺", 1
    WOOD_GATHERING_POST = "목재 채취장", "🌲🏭", 1
    EARTH_GATHERING_POST = "토석 채취장", "🏞️🏭", 1
    BUILDING_MATERIAL_FACTORY = "건축자재 공장", "🧱🏭", 1
    RECRUITING_CAMP = "모병소", "🛡️🏭", 1
    SUPPLY_BASE = "보급기지", "🏭🤖", 1
    CLINIC = "진료소", "🏥", 1
    
    @classmethod
    def get_basic_facility_list(cls) -> list["FacilityCategory"]:
        return [
            cls.FRESH_WATER_SOURCE,
            cls.HUNTING_GROUND,
            cls.PASTURELAND,
            cls.GATHERING_POST
        ]
    
    @classmethod
    def get_ramdom_base_facility_category(cls) -> "FacilityCategory":
        return random.choice(cls.get_basic_facility_list())
    
    @classmethod
    def get_advanced_facility_list(cls) -> list["FacilityCategory"]:
        rtn = [comp for comp in cls if comp.level == 1]
        return rtn

class Strategy(ArislenaEnum):
    PASS = "속행", "⏩"
    SHOCK = "충격", "💥"
    FIREPOWER = "화공", "🔥"
    FIERCENESS = "맹공", "🦁"
    DEFENSE = "방비", "🛡️"
    ENCIRCLEMENT = "포위", "🔗"
    RETREAT = "후퇴", "🏳️"

class CommandCategory(ArislenaEnum):
    UNSET = "미정", "❓", -1
    RECRUIT = "모병", "🛡️"
    SCOUT = "정찰", ":eye:"
    RETREAT = "후퇴", ":runner:"
    TRAIN = "훈련", ":muscle:"

class D9Judge(ArislenaEnum):
    TRAGIC = "처참함", "😭"
    AVERAGE = "무난함", "😐"
    SUCCESS = "성공", "✅"
    GREAT_SUCCESS = "멋지게 성공!", "🎉"

class D20Judge(ArislenaEnum):
    TRAGIC = "처참함", "😭"
    POOR = "아쉬움", "😔"
    AVERAGE = "무난함", "😐"
    PROPER = "적절함", "😊"
    SUCCESS = "성공", "✅"
    GREAT_SUCCESS = "멋지게 성공!", "🎉"

class WorkerCategory(ArislenaEnum):
    UNSET = "미정", "❓", -1
    CREW = "대원", "👥",
    LIVESTOCK = "가축", "🐄"

class WorkCategory(ArislenaEnum):
    UNSET = "미정", "❓", -1
    IRRIGATION = "관개", "🚰"
    HUNTING = "사냥", "🏹"
    GATHERING = "채집", "👐"
    AGRICULTURE = "농경", "🌾"
    FIGHTING = "전투", "⚔️"
    CONSTRUCTION = "건설", "🏗️"
    MANUFACTURING = "제조", "🏭"
    TREAT = "치료", "🩹"
    
    @classmethod
    def to_list(cls) -> list["WorkCategory"]:
        """
        UNSET을 제외한 모든 ExperienceCategory를 반환함
        """
        return [component for component in cls if component != cls.UNSET]

class WorkerHPState(ArislenaEnum):
    # 0: 건강, 1: 경상, 2: 중상, 3: 사망
    HEALTHY = "건강", "🟢"
    INJURED = "경상", "🟡"
    CRITICAL = "중상", "🔴"
    DEAD = "사망", "⚰️"
    
    # 최대 HP에 대한 현재 HP 비율에 따른 판정
    # >= 90%: 건강
    # >= 50%: 경상
    # < 50%: 중상
    # 0: 사망

