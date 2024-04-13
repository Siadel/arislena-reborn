from pathlib import Path
import json

from box import Box

from py_base.utility import JSON_DIR, UTF8

# json 데이터 저장하기
def dump_json(data: dict, file_name: str) -> None:
    file_path = Path(JSON_DIR, file_name)
    with open(file_path, "w", encoding=UTF8) as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# json 데이터 불러오기
def load_json(file_name: str, **kwargs) -> dict|list:
    file_path = Path(JSON_DIR, file_name)
    if file_path.exists() == False: return {}
    with open(file_path, "r", encoding=UTF8) as file:
        return json.load(file, **kwargs)

def setdefault_json(data: dict[str, dict], file_name: str) -> None:
    """
    json 파일을 불러오고, 데이터를 추가하고, 저장
    """
    load_data = load_json(file_name)
    for key, value in data.items():
        load_data.setdefault(key, value)
    dump_json(load_data, file_name)

def load_box(file_name:str) -> Box:
    """
    json 파일을 box 객체로 불러옴
    """
    if not file_name.endswith(".json"):
        file_name += ".json"
    return Box(
        load_json(file_name),
        default_box=False
    )

def dump_box(data: Box, file_name:str) -> None:
    """
    box 객체를 json 파일로 저장함
    """
    if not file_name.endswith(".json"):
        file_name += ".json"
    dump_json(dict(data), file_name)