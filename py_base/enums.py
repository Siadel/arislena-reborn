"""
상태를 나타내는 모듈 (모든 상태가 한데 모여있음)
"""
import enum

# 스케줄 상태
class Schedule(enum.IntEnum):
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