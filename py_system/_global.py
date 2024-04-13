"""
py_system, cog 등의 모듈에서 공통적으로 사용하는 전역 변수들
"""

import re
from py_base import jsonobj

bot_setting = jsonobj.BotSetting.from_json_file()
setting_by_guild = jsonobj.SettingByGuild.from_json_file()
dice_memory = jsonobj.DiceMemory.from_json_file() # TODO 여러 서버에서 사용할 수 있도록 사용 로직 수정 필요
translate = jsonobj.Translate.from_json_file() # TODO 여러 서버에서 사용할 수 있도록 사용 로직 수정 필요


# 한글, 영문, 숫자, 공백만 허용하는 정규식
name_regex = re.compile(r"[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9 ]")
