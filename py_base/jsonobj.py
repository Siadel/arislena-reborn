"""
json 파일과 연동되는 클래스들\n
json 파일을 불러오고, 저장하고, 수정하는 기능을 제공함
"""
from typing import ClassVar
from dataclasses import dataclass
import datetime

from py_base.abstract import JsonObject, FluidJsonObject
from py_base.utility import DATE_EXPRESSION

# schedule
@dataclass
class Schedule(JsonObject):
    '''
    - start_date : 시작 날짜
    - now_turn : 게임 진행 턴 수
    - state : 현재 상태(0: 시작 대기, 1: 게임 중, 2: 중단, 3: 종료)
    '''
    start_date: str = (datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)
    end_date: str = ""
    now_turn: int = 0
    state: int = 0

    file_name: ClassVar[str] = "schedule.json"

@dataclass
class SettingByGuild(JsonObject):
    announce_location: dict[str, int]
    user_role_id: dict[str, int]
    admin_role_id: dict[str, int]

    file_name: ClassVar[str] = "setting_by_guild.json"

@dataclass
class GameSetting(JsonObject):
    test_mode: bool
    admin_mode: bool
    arislena_end_turn: int
    cron_days_of_week: str
    cron_hour: int
    name_length_limit: int

    file_name: ClassVar[str] = "game_setting.json"

@dataclass
class BotSetting(JsonObject):
    main_guild_id: int
    guild_ids: list[int]
    application_id: int

    file_name: ClassVar[str] = "bot_setting.json"

@dataclass(init=False)
class DiceMemory(FluidJsonObject):
    file_name: ClassVar[str] = "dice_memory.json"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass(init=False)
class Translate(FluidJsonObject):
    file_name: ClassVar[str] = "translate.json"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def get_from_map(self, map_key:str, key:str, table_name:str=None, default=None):
        """
        json/translate.json에서 영문 key에 대응되는 한국어 value를 반환함
        """
        tr_map:dict = self.get(map_key)
        if isinstance(table_name, str) and table_name in tr_map and key in tr_map[table_name]:
            return tr_map[table_name][key]
        elif key in tr_map["general"]:
            return tr_map["general"][key]
        else:
            return default

# @dataclass
# class Sign_up_waitlist:
#     owner:str
#     owner_ID:int
#     nation_name:str

#     @classmethod
#     def get_waitlists(cls):
#         # waitlist.json에서 데이터를 가져옴
#         data = jsonwork.load_json("sign_up_waitlist.json")
#         return [cls(**d) for d in data]
    
#     @classmethod
#     def delete_waitlist(cls, owner_ID:int):
#         # waitlist.json에서 데이터를 삭제
#         data = jsonwork.load_json("sign_up_waitlist.json")
#         for d in data:
#             if d['owner_ID'] == owner_ID:
#                 data.remove(d)
#                 break
#         jsonwork.dump_json(data, "sign_up_waitlist.json")
    
#     def add(self):
#         # waitlist.json에 데이터를 저장
#         data = jsonwork.load_json("sign_up_waitlist.json")
#         data.append(self.__dict__)
#         jsonwork.dump_json(data, "sign_up_waitlist.json")

# @dataclass
# class Fate:
#     ID : int = 0
#     category: str = ""
#     description: str = ""
#     victory_condition: str = ""
#     lose_condition: str = ""
#     note: str = ""

#     @classmethod
#     def get_fate(cls, category:str):
#         # fate.json에서 데이터를 가져옴
#         data = jsonwork.load_json("fate.json")
#         for d in data:
#             if d['category'] == category:
#                 return cls(**d)
#         raise Exception(f"해당하는 운명이 없습니다. ({category})")
    
#     @classmethod
#     def get_all_categories(cls):
#         # fate.json에서 데이터를 가져옴
#         data = jsonwork.load_json("fate.json")
#         return [d['category'] for d in data]
    
#     def dump(self):
#         # fate.json에 데이터를 저장
#         jsonwork.dump_json(self.__dict__, "fate.json")

#     def add(self):
#         # fate.json에 데이터를 저장
#         data = jsonwork.load_json("fate.json")
#         data.append(self.__dict__)
#         jsonwork.dump_json(data, "fate.json")
