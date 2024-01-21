import re

from py_system.database import MainDB
from py_system import jsonobj

main_db = MainDB()
settings = jsonobj.Settings()

# 특수문자 정규식
name_ban = re.compile(r"\W")