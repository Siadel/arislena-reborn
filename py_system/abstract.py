from abc import ABCMeta, abstractmethod

from py_base import jsonwork

class TableObject(metaclass=ABCMeta):
    """
    테이블 오브젝트 (db 파일의 table로 저장되는 녀석들)
    """

    def __iter__(self):
        rtn = list(self.items.values())
        rtn.pop(0) # ID 제거
        return iter(rtn)
    
    @property
    def items(self):
        # __slots__는 tuple
        return {slot : self.__getattribute__(slot) for slot in self.__slots__}

    @classmethod
    def get_table_name(cls):
        """
        테이블명은 클래스명과 동일함
        """
        return cls.__name__

    @classmethod
    def get_column_set(cls):
        """
        테이블의 컬럼명을 집합으로 반환
        """
        return set(cls.__annotations__.keys())
    
    @property
    def keys_string(self) -> str:
        keys = list(self.__slots__)
        keys.remove("ID")
        return ", ".join(keys)
    
    @property
    def values_string(self) -> str:
        """
        id를 제외한 모든 attribute 값을 문자열로 반환
        """
        values = list(self.items.values())
        values.pop(0)
        string = ", ".join([f"'{value}'" if isinstance(value, str) else str(value) for value in values])
        string = string.replace("None", "NULL")
        return string
    
    def get_wildcard_string(self) -> str:
        """
        sql문에서 ?를 채우기 위한 문자열 반환
        """
        return ", ".join(["?" for i in range(len(self.__slots__) - 1)])
    
    @classmethod
    def get_create_table_string(cls) -> str:
        """
        sql문에서 테이블 생성을 위한 문자열 반환
        """
        sql = f"CREATE TABLE IF NOT EXISTS {cls.get_table_name()} ("
        for key in cls.__annotations__.keys():
            if key == "ID":
                sql += f"{key} INTEGER PRIMARY KEY AUTOINCREMENT, "
            else:
                sql += f"{key} {cls.get_column_type(key)}, "
        sql = sql[:-2] + ")"
        return sql
    
    @classmethod
    def get_column_type(cls, column_name:str) -> str:
        """
        sql문에서 쓰는 컬럼의 데이터 형식을 반환
        """
        value = cls.__annotations__[column_name]
        if "str" in str(value).lower():
            return "TEXT"
        elif "int" in str(value).lower():
            return "INTEGER"
        elif "float" in str(value).lower():
            return "REAL"
        else:
            raise Exception("SQL에서 사용할 수 없는 데이터 형식입니다. (str, int, float 중 하나를 사용해주세요.)")
        
    @property
    def en_kr_dict(self) -> dict[str, str]:
        # 영어 : 한국어
        return dict(zip(self.__slots__, self.kr_list))
    
    @property
    def kr_dict(self) -> dict[str, str]:
        # 한국어 : 대응되는 attribute 값
        return dict(zip(self.kr_list, self.items.values()))
    
    @property
    def kr_dict_without_id(self) -> dict[str, str]:
        # 한국어 : 대응되는 attribute 값
        return dict(zip(self.kr_list[1:], list(self.items.values())[1:]))
    
    @property
    @abstractmethod
    def kr_list(self) -> list[str]:
        pass
    
    def __post_init__(self):
        """
        display_main : 버튼을 통해 열람할 때, 메인으로 표시할 컬럼명 (주로 name)
        display_sub : 버튼을 통해 열람할 때, 서브로 표시할 컬럼명 (주로 ID)
        """
        self.display_main = "name"
        self.display_sub = "ID"

class JsonObject(metaclass=ABCMeta):
    """
    json 파일과 연동되는 클래스들의 부모 클래스
    """

    def __init__(self, file_name:str, monodepth:bool = False):
        """
        file_name : json 파일 이름 (확장자 포함)
        monodepth : json 파일이 단일 깊이로 되어있는지 여부
        self.content : json 파일의 내용
        ---
        monodepth가 True일 경우, json 파일에 있는 데이터를 attr로 저장함
        """
        self.file_name = file_name
        self.monodepth = monodepth
        self.content = jsonwork.load_json(file_name)

        if monodepth:
            for key, value in self.content.items():
                setattr(self, key, value)
    
    def __del__(self):
        self.dump()

    def dump(self):
        """
        json 파일에 현재 데이터를 저장함\n
        monodepth가 True일 경우, 별도의 attr로 저장된 데이터를 self.content에 저장한 뒤 json 파일에 저장함
        """
        if self.monodepth:
            for key in self.content.keys():
                self.content[key] = getattr(self, key)
        jsonwork.dump_json(self.content, self.file_name)

    def update(self, key, value):
        """
        json 파일에 있는 데이터를 수정함
        """
        self.content[key] = value
        self.dump()

    def delete_one(self, key):
        """
        json 파일에서 key에 해당하는 값을 삭제함
        """
        self.content.pop(key)
        self.dump()