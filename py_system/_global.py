"""
py_system, cog 등의 모듈에서 공통적으로 사용하는 전역 변수들
"""

import re

from py_base import jsonobj
from py_base.dbmanager import MainDB
from py_base.schedule_manager import ScheduleManager


bot_setting = jsonobj.BotSetting.from_json_file()
game_setting = jsonobj.GameSetting.from_json_file()
setting_by_guild = jsonobj.SettingByGuild.from_json_file()
schedule = jsonobj.Schedule.from_json_file()
dice_memory = jsonobj.DiceMemory.from_json_file()
translate = jsonobj.Translate.from_json_file()

main_db = MainDB(test_mode=game_setting.test_mode)
schedule_manager = ScheduleManager(main_db, schedule, game_setting)

# 한글, 영문, 숫자, 공백만 허용하는 정규식
name_regex = re.compile(r"[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9 ]")
