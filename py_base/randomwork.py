"""
주사위가 아닌 확률을 이용한 랜덤 모듈
"""
import jsonwork
import random

def check_sum(ratio:dict):
    """
    value의 합이 1인지 확인
    """
    result = round(sum(ratio.values()), 4)
    if result != 1:
        return result
    return True

def ratio_processing(ratio:dict):

    processed = {}
    idx = 0
    for k, v in ratio.items():
        processed.setdefault(k, [0, v])
        if idx > 0:
            processed[k][0] = processed[str(int(k)-1)][1]
            processed[k][1] += processed[k][0]
        # 부동소수점 해결
        processed[k][0] = round(processed[k][0], 4)
        processed[k][1] = round(processed[k][1], 4)
        idx += 1

    return processed

# ratios.json 파일을 읽어서 각각의 ratio를 ratio_processing 함수를 이용하여 처리한 후 RATIO_TABLE 딕셔너리에 저장
RATIO_TABLE: dict[str, dict] = {}
for k, v in jsonwork.load_json('ratio_table.json').items():
    RATIO_TABLE[k] = ratio_processing(v)

def generate_stats(key:str, trial:int=1) -> list | str:
    """
    RATIO_TABLE 딕셔너리의 key를 인자로 받아, 해당 key의 확률표를 이용해 랜덤하게 선택된 value를 반환
    """
    table = RATIO_TABLE[key]
    def try_once():
        rand = random.random()
        for k, v in table.items():
            if v[0] <= rand and rand < v[1]:
                return k
    if trial > 1:
        return [try_once() for _ in range(trial)]
    else:
        return try_once()
