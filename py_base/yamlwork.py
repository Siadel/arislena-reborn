from pathlib import Path
import yaml

from py_base.utility import YAML_DIR, UTF8

def load_yaml(file_name: str) -> dict|list:
    file_path = Path(YAML_DIR, file_name)
    if file_path.exists() == False: return {}
    with open(file_path, "r", encoding=UTF8) as file:
        return yaml.safe_load(file)

def dump_yaml(data: dict, file_name: str) -> None:
    file_path = Path(YAML_DIR, file_name)
    with open(file_path, "w", encoding=UTF8) as file:
        yaml.dump(data, file, allow_unicode=True, default_flow_style=False, sort_keys=False)