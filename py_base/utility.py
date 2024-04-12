"""
파일 경로, 유틸리티 함수 모음 모듈
"""
from typing import Any
import datetime
import os
from enum import Enum

UTF8 = "utf-8"

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

PYTHON_SQL_DTYPE_MAP = {
    "str": "TEXT",
    "int": "INTEGER",
    "float": "REAL",
    "none": "NULL",
    "extint": "INTEGER",
    "enum": "INTEGER",
    "bool": "INTEGER"
}

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

def sql_type(value: Any) -> str:
    
    for k, v in PYTHON_SQL_DTYPE_MAP.items():
        if k in str(type(value)).lower():
            return v
    raise Exception(f"Type {type(value)} is not supported in Arislena's SQL.")

def sql_value(value: str | Enum | None | int | float) -> str:
    """
    Convert a Python value to its SQL representation.

    Args:
        value (Union[str, int, float, None]): The Python value to be converted.

    Returns:
        str: The SQL representation of the value.

    Raises:
        None

    Examples:
        >>> sql_value("John")
        "'John'"
        >>> sql_value(42)
        '42'
        >>> sql_value(3.14)
        '3.14'
        >>> sql_value(None)
        'NULL'
        >>> class MyEnum(Enum):
        ...     VALUE = 1
        >>> sql_value(MyEnum.VALUE)
        '1'
    """
    if isinstance(value, str):
        return f"'{value}'"
    if isinstance(value, Enum):
        return str(value.value)
    elif value is None:
        return "NULL"
    else:
        return str(value)

    # if isinstance(value, str):
    #     return f"'{value}'"
    # elif value is None:
    #     return "NULL"
    # else:
    #     return str(value)