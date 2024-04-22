"""
파일 경로, 유틸리티 함수 모음 모듈
"""
import datetime
import os
from pathlib import Path
from typing import Any
from enum import Enum

UTF8 = "utf-8"

APOSTROPHE = "'"
DOUBLE_QUOTE = '"'
ENTER = "\n"
DOUBLE_ASTERISK = "**"

DATE_EXPR = "%Y-%m-%d"
FULL_DATE_EXPR = "%Y-%m-%d %H:%M:%S"
FULL_DATE_EXPR_2 = "%Y-%m-%d_%H-%M-%S"

# CWD = os.getcwd().replace("\\", "/") + "/"
# refactoring
CWD = Path(os.getcwd())
current_dir = os.path.dirname(__file__).replace("\\", "/") + "/"
#if "ghftr" in os.getcwd(): current_path = LOCAL_PATH
#elif "workspace" in os.getcwd(): current_path = GROOM_PATH
#else: raise ValueError("작업 환경을 다시 확인해주세요.")

JSON_DIR = Path(CWD, "json")
DATA_DIR = Path(CWD, "data")
BACKUP_DIR = Path(CWD, "backup")
LOCALIZATION = Path(CWD, "localization")

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

def sql_type(dtype: type) -> str:
    """
    python dtype을 SQL dtype으로 변환
    """
    
    annotation = str(dtype).removeprefix("<").removesuffix(">").split("'")
    ref_class = annotation[0].strip()
    class_name = annotation[1].strip()
    
    match (ref_class, class_name):
        
        case (_, "str"): return "TEXT"
        case (_, "int"): return "INTEGER"
        case (_, "float"): return "REAL"
        case (_, "NoneType"): return "NULL"
        case (_, "bool"): return "INTEGER"
        case (_, "enum.EnumType"): return "TEXT"
        case (_, "py_base.datatype.ExtInt"): return "INTEGER"
        case ("enum", _): return "INTEGER"
        
        case _: Exception(f"Type {type(dtype)} is not supported in Arislena's SQL.")

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