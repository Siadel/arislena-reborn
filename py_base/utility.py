"""
전역 변수, 파일 경로, 유틸리티 함수 모음 모듈
"""
import datetime
import os

APOSTROPHE = "'"
DOUBLE_QUOTE = '"'
ENTER = "\n"
DOUBLE_ASTERISK = "**"

DATE_EXPRESSION = "%Y-%m-%d"
DATE_EXPRESSION_FULL = "%Y-%m-%d %H:%M:%S"
DATE_EXPRESSION_FULL_2 = "%Y-%m-%d_%H-%M-%S"

current_path = os.getcwd().replace("\\", "/") + "/"
current_dir = os.path.dirname(__file__).replace("\\", "/") + "/"
#if "ghftr" in os.getcwd(): current_path = LOCAL_PATH
#elif "workspace" in os.getcwd(): current_path = GROOM_PATH
#else: raise ValueError("작업 환경을 다시 확인해주세요.")

JSON_DIR = current_path + "json/"
DATA_DIR = current_path + "data/"
BACKUP_DIR = current_path + "backup/"

def get_date(date_expression="%Y-%m-%d"):
    timezone = datetime.timezone(datetime.timedelta(hours=9))
    return datetime.datetime.now(timezone).strftime(date_expression)

def swap_dict(dictionary:dict):
    return {value:key for key, value in dictionary.items()}

def wrap(word:str, wrapper:str=""):
    """
    word 양옆에 wrapper를 붙여서 반환
    """
    if wrapper == "": return word
    return wrapper + word + wrapper

