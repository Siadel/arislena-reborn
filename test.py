import yaml
import pprint

with open("yaml/detail.yaml", "r", encoding="utf-8") as stream:
    print(type(yaml.safe_load(stream)))