"""
파일 경로, 유틸리티 함수 모음 모듈
"""
import datetime, re
from pathlib import Path
from enum import Enum
from numpy import random as np_random

UTF8 = "utf-8"

APOSTROPHE = "'"
DOUBLE_QUOTE = '"'
ENTER = "\n"
DOUBLE_ASTERISK = "**"

DATE_FORMAT = "%Y-%m-%d"
FULL_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
FULL_DATE_FORMAT_NO_SPACE = "%Y-%m-%d_%H-%M-%S"

CWD = Path.cwd()

JSON_DIR = Path(CWD, "json")
YAML_DIR = Path(CWD, "yaml")
DATA_DIR = Path(CWD, "data")
BACKUP_DIR = Path(CWD, "backup")
LOCALIZATION = Path(CWD, "localization")

# 한글, 영문, 숫자, 공백만 허용하는 정규식
name_regex = re.compile(r"[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9 ]")

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
    

def sql_value(value: str | Enum | None | int | float | bool) -> str:
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
    elif isinstance(value, bool):
        return str(int(value))
    elif value is None:
        return "NULL"
    else:
        return str(value)

def select_from_subclasses(_class: type, **query) -> type:
    """
    _class의 서브클래스 중 클래스 변수로 a=b 꼴의 query식 중 하나라도 만족하는 서브클래스를 반환합니다.
    
    조건을 만족하는 복수의 서브클래스가 존재할 경우, _class.__subclasses__() 메소드로 불러온 리스트 중 조건을 만족하는 첫 번째 서브클래스를 반환합니다.
    """
    
    for subclass in _class.__subclasses__():
        for key, value in query.items():
            if getattr(subclass, key) == value:
                return subclass
    raise ValueError(f"No subclass of {_class} matches the query {query}; {_class.__subclasses__()}")

def get_minus4_to_4() -> int:
    """
    -4 ~ 4 사이의 정수를 대한민국 수능 9등급식 정규분포 근사 논리로 반환합니다.
    """
    return np_random.choice([-4, -3, -2, -1, 0, 1, 2, 3, 4], p=[0.04, 0.07, 0.12, 0.17, 0.20, 0.17, 0.12, 0.07, 0.04])