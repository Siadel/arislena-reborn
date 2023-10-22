"""
json 파일과 연동되는 클래스들\n
json 파일을 불러오고, 저장하고, 수정하는 기능을 제공함
"""

from abc import ABCMeta
from dataclasses import dataclass
import datetime
import os

from py_base import jsonwork, utility

class JsonObject(metaclass=ABCMeta):
    """
    json 파일과 연동되는 클래스들의 부모 클래스
    """

    def __init__(self, file_name:str, monodepth:bool = False):
        """
        file_name : json 파일 이름 (확장자 포함)
        monodepth : json 파일이 단일 깊이로 되어있는지 여부
        self.content : json 파일의 내용
        ---
        monodepth가 True일 경우, json 파일에 있는 데이터를 attr로 저장함
        """
        self.file_name = file_name
        self.monodepth = monodepth
        self.content = jsonwork.load_json(file_name)

        if monodepth:
            for key, value in self.content.items():
                setattr(self, key, value)
    
    def __del__(self):
        self.dump()

    def dump(self):
        """
        json 파일에 현재 데이터를 저장함\n
        monodepth가 True일 경우, 별도의 attr로 저장된 데이터를 self.content에 저장한 뒤 json 파일에 저장함
        """
        if self.monodepth:
            for key in self.content.keys():
                self.content[key] = getattr(self, key)
        jsonwork.dump_json(self.content, self.file_name)

    def update(self, key, value):
        """
        json 파일에 있는 데이터를 수정함
        """
        self.content[key] = value
        self.dump()

    def delete_one(self, key):
        """
        json 파일에서 key에 해당하는 값을 삭제함
        """
        self.content.pop(key)
        self.dump()

class Keys(JsonObject):

    def __init__(self):
        super().__init__("keys.json", True)
        self.main_guild_id:int
        self.guild_ids:list
        self.application_id:int
        self.token:str

# schedule
class Schedule(JsonObject):
    '''
    - start_date : 시작 날짜
    - now_turn : 게임 진행 턴 수
    - state : 현재 상태(0: 시작 대기, 1: 게임 중, 2: 중단, 3: 종료)
    '''
    def __init__(self):
        super().__init__("schedule.json", True)
        self.start_date: str
        self.end_date: str
        self.now_turn: int
        self.state: int

        if not os.path.isfile(utility.JSON_DIR + 'schedule.json'):
            json_data = self.get_init_data()
            jsonwork.dump_json(json_data, 'schedule.json')

    @staticmethod
    def get_init_data():
        return {
            "start_date" : f'{(datetime.date.today() + datetime.timedelta(days=1)).strftime(utility.DATE_EXPRESSION)}',
            "end_date" : "",
            "now_turn" : 0,
            "state" : 0
            }

# settings
class Settings(JsonObject):

    def __init__(self):
        super().__init__("settings.json", True)
        self.test_mode:bool
        self.admin_mode:bool
        self.arislena_end_turn: int
        self.cron_days_of_week: str
        self.cron_hour: str

# translation
class Translation(JsonObject):

    def __init__(self):
        super().__init__("translation.json", False)


# dummy

class DiceMemory(JsonObject):

    def __init__(self):
        """
        주사위를 저장하는 파일
        """
        super().__init__("dice_memory.json")

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
