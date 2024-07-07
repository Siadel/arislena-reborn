import random

from py_base.abstract import YamlObject

class Detail(YamlObject):
    file_name: str = "detail.yaml"
    
    def __init__(self):
        super().__init__()
    
    def get_random_detail(self, enum_component_name) -> str:
        return random.choice(self.data["CrewDetail"][enum_component_name])
        
    def get_random_worker_descriptions(self, sample_count:int) -> list[str]:
        # 무작위로 sample_count개 분류를 선택하고, 그 중에서 무작위로 1개의 성격을 선택한다.
        # 파일의 CrewDesctription을 참조하여 성격을 선택한다.
        
        crew_description: dict = self.data["CrewDescription"]
        
        desc_category = random.sample(list(crew_description.keys()), k=sample_count)
        descriptions = [random.choice(crew_description[category]) for category in desc_category]
        
        return descriptions

class TableObjTranslator(YamlObject):
    file_name: str = "tableobj_translate.yaml"
    
    def __init__(self):
        super().__init__()
        
    def get(self, key:str, table_name:str=None, default=None):
        """
        yaml/translate.yaml에서 key에 대응되는 value를 반환함
        """
        if isinstance(table_name, str) and table_name in self.data and key in self.data[table_name]:
            return self.data[table_name][key]
        elif key in self.data["general"]:
            return self.data["general"][key]
        else:
            return default