"""
utility와 비슷한 기능을 하지만, 에러 메세지를 출력하는 함수를 모아놓은 모듈
"""
from py_base import utility
from py_discord import warning

def below0(value:int):
    """
    value가 0보다 작으면 AriWarning을 발생시키는 함수
    """
    if utility.is_below0(value):
        raise warning.Default("0보다 작은 값입니다.")