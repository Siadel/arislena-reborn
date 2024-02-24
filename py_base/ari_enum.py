"""
상태를 나타내는 모듈 (모든 상태가 한데 모여있음)
"""
import enum

def get_enum(annotation:str, value:int) -> enum.IntEnum:
    """
    enum을 반환함
    """
    enum_class = annotation.split("'")[1]
    return globals()[enum_class](value)

# 스케줄 상태
class ScheduleState(enum.IntEnum):
    # 0: 시작 대기, 1: 게임 중, 2: 중단, 3: 종료
    WAITING = 0
    ONGOING = 1
    PAUSED = 2
    ENDED = 3

class Color(enum.IntEnum):
    RED = 0xFF0000
    ORANGE = 0xFFA500
    YELLOW = 0xFFFF00
    GREEN = 0x00FF00
    BLUE = 0x0000FF
    INDIGO = 0x4B0082
    VIOLET = 0xEE82EE

class User(enum.IntEnum):
    BEFORE_START = 0
    AFTER_START = 1

# 범용 예, 아니요
class YesNo(enum.IntEnum):
    YES = 1
    NO = 0

# 부대 상태
class Troop(enum.IntEnum):
    IDLE = 0
    ALERT = 1
    FORTIFYING = 2
    MOVING = 3
# 블럭 상태
class Block(enum.IntEnum):
    SAFE = 0
    CRISIS = 1
    CONQUERED = 2
# 건물 상태
class Building(enum.IntEnum):
    ONGOING_CONSTRUCTION = 0
    COMPLETED = 1
    PILLAGED = 2
# 기술 상태
class Technology(enum.IntEnum):
    ONGOING_RESEARCH = 0
    COMPLETED = 1
    SABOTAGED = 2


# 인구 분류
class HumanClass(enum.IntEnum):
    # 0: 일반인력, 1: 고급인력
    COMMON = 0
    ADVANCED = 1

class HumanSex(enum.IntEnum):
    # 0: 남성, 1: 여성
    MALE = 0
    FEMALE = 1

class TerritorySafety(enum.IntEnum):
    # 회색, 흑색, 적색, 황색, 녹색
    # 회색 : 미확인
    # 흑, 적, 황, 녹 순으로 안전
    UNKNOWN = 0
    BLACK = 1
    RED = 2
    YELLOW = 3
    GREEN = 4
    