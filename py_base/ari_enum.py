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
    TRAINING = "훈련 중", "🏋️"
    LABORING = "일하는 중", "🛠️", 1
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
    SPADES = "지휘력", ":spades_ari:"
    DIAMONDS = "생산력", ":diamonds:"
    HEARTS = "필수자원", ":hearts:"
    CLUBS = "고급자원", ":four_leaf_clover:"
    GOLD = "금", ":coin:"
    
    @classmethod
    def to_list(cls) -> list["ResourceCategory"]:
        return [component for component in cls if component.value != cls.UNSET.value]

class FacilityCategory(ArislenaEnum):
    UNSET = "미정", "❓", -1
    HEADQUARTER = "회관", "🏰"
    HABITATION = "거주지", "🏠"
    GATHERING_SITE = "채집지", "👐"
    HUNTING_GROUND = "수렵지", "🏹"
    TRAINING_CAMP = "훈련소", "🎯"
    BARRACK = "병영", ":muscle:", 1
    FARMLAND = "농경지", "🌾", 1
    WALL = "방벽", "🧱", 1
    LIVESTOCK_FARM = "축사", "🐄🏠", 1
    INFIRMARY = "치료소", "🏥", 1
    GOLD_MINE = "금광", "💰⚒️", 1
    LAB = "연구소", "🔬", 2
    MARKET = "시장", "🏪", 2
    FORGE = "대장간", "🔨", 2
    RECON_POST = "정찰기지", "🔭", 2
    
    @classmethod
    def get_list_by_tier(cls, tier: int) -> list["FacilityCategory"]:
        return [comp for comp in cls if comp.level == tier]

class ExperienceCategory(ArislenaEnum):
    UNSET = "미정", "❓", -1
    HUNTING = "사냥", "🏹"
    GATHERING = "채집", "👐"
    AGRICULTURE = "농경", "🌾"
    PASTURING = "목축", "🐄"
    COMBAT = "전투", "⚔️"
    STRATEGY = "전략", "🧠"
    ADMINISTRATION = "행정", "📜"
    CONSTRUCTION = "건설", "🏗️"
    MANUFACTURING = "제조", "🏭"
    PHARMACY = "약학", "💊"
    
    @classmethod
    def to_list(cls) -> list["ExperienceCategory"]:
        """
        UNSET을 제외한 모든 ExperienceCategory를 반환함
        """
        return [component for component in cls if component != cls.UNSET]

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
    DEPLOY = "배치", "👇"
    RECRUIT = "모병", "🛡️"
    SCOUT = "정찰", ":eye:"
    RETREAT = "후퇴", ":runner:"
    TRAIN = "훈련", ":muscle:"



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

class DeployAs(ArislenaEnum):
    WORKER = "종사자", "👷"
    VISITOR = "방문자", "👤"