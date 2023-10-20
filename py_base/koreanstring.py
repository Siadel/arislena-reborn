"""
한국어 문자열을 처리하는 함수 모듈
"""
from py_base import HangeulLogic
from py_base.utility import wrap

def has_coda(word:str):
    # 마지막 글자가 받침이 있는지 확인
    # 한글이 아니면 None 반환
    syllable = HangeulLogic.Syllable(word[-1])
    return syllable.has_coda()

# 주격 (이/가)
def nominative(word:str, wrapper:str=""):
    # coda가 True면 word + "이"를 반환
    # False면 word + "가"를 반환
    if has_coda(word) is None:
        return word
    if has_coda(word):
        return wrap(word, wrapper) + "이"
    else:
        return wrap(word, wrapper) + "가"

# 목적격 (을/를)
def objective(word:str, wrapper:str=""):
    # coda가 True면 word + "을"를 반환
    # False면 word + "를"를 반환
    if has_coda(word) is None:
        return word
    if has_coda(word):
        return wrap(word, wrapper) + "을"
    else:
        return wrap(word, wrapper) + "를"

# 주제 (은/는)
def topicmarker(word:str, wrapper:str=""):
    # coda가 True면 word + "은"를 반환
    # False면 word + "는"를 반환
    if has_coda(word) is None:
        return word
    if has_coda(word):
        return wrap(word, wrapper) + "은"
    else:
        return wrap(word, wrapper) + "는"

# 공동격
def joint(word:str, wrapper:str=""):
    # coda가 True면 word + "과"를 반환
    # False면 word + "와"를 반환
    if has_coda(word) is None:
        return word
    if has_coda(word):
        return wrap(word, wrapper) + "과"
    else:
        return wrap(word, wrapper) + "와"

# 도구격 (으로/로)
def instrumental(word:str, wrapper:str=""):
    # coda가 True면 word + "으로"를 반환
    # False면 word + "로"를 반환
    if has_coda(word) is None:
        return word
    if has_coda(word):
        return wrap(word, wrapper) + "으로"
    else:
        return wrap(word, wrapper) + "로"

def check_vaild_char(char:str):
    if HangeulLogic.Syllable(char).classification not in ["한글", "숫자", "영문"]:
        return False
    return True