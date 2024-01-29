"""
json 파일과 연동되는 클래스들\n
json 파일을 불러오고, 저장하고, 수정하는 기능을 제공함
"""
import datetime
import os

from py_base import jsonwork, utility
from py_system.abstract import JsonObject

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
