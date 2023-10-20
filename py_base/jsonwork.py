import os
import json

from py_base import utility

# json 데이터 저장하기
def dump_json(data: dict, filename: str) -> None:
    path = utility.JSON_DIR + filename
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# json 데이터 불러오기
def load_json(filename: str) -> dict|list:
    path = utility.JSON_DIR + filename
    if os.path.exists(path) is False:
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def setdefault_json(data: dict[str, dict], filename: str) -> None:
    """
    json 파일을 불러오고, 데이터를 추가하고, 저장
    """
    path = utility.JSON_DIR + filename
    load_data = load_json(filename)
    for key, value in data.items():
        load_data.setdefault(key, value)
    with open(path, "r", encoding="utf-8") as file:
        json.dump(load_data, file, ensure_ascii=False, indent=4)