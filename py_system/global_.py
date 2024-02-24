"""
py_system, cog 등의 모듈에서 공통적으로 사용하는 전역 변수들
"""

import re

from py_base.jsonobj import SettingByGuild, GameSetting, BotSetting, Schedule, DiceMemory
from py_base.dbmanager import MainDB
from py_system.schedule_manager import ScheduleManager


bot_setting = BotSetting.from_json_file()
game_setting = GameSetting.from_json_file()
setting_by_guild = SettingByGuild.from_json_file()
schedule = Schedule.from_json_file()
dice_memory = DiceMemory.from_json_file()

main_db = MainDB(test_mode=game_setting.test_mode)
schedule_manager = ScheduleManager(main_db, schedule, game_setting)

# 한글, 영문, 숫자, 공백만 허용하는 정규식
name_regex = re.compile(r"[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9 ]")
