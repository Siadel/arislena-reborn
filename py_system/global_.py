"""
py_system, cog 등의 모듈에서 공통적으로 사용하는 전역 변수들
"""

import re

from py_base.jsonwork import load_box
from py_base.dbmanager import MainDB
from py_system.schedule_manager import ScheduleManager
from py_system import jsonobj


game_settings = load_box("game_settings.json")
bot_settings = load_box("bot_settings.json")
keys = load_box("keys.json")
schedule = jsonobj.Schedule()

main_db = MainDB(test_mode=game_settings.test_mode)

# 한글, 영문, 숫자, 공백만 허용하는 정규식
name_regex = re.compile(r"[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9 ]")

schedule_manager = ScheduleManager(main_db, schedule, game_settings)