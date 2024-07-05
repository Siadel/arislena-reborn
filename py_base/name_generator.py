from py_base import yamlwork

import random

korean_name_file: dict = yamlwork.load_yaml('korean_name.yaml')

def get_random_name(sex_int: int) -> str:
    return random.choice(korean_name_file[sex_int])

def get_random_family_name() -> str:
    return random.choice(korean_name_file["family_name"])

def get_random_full_name(sex_int: int) -> str:
    return f"{get_random_family_name()}{get_random_name(sex_int)}"