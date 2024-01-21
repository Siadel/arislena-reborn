from abc import ABCMeta, abstractmethod

class IntValueObject(metaclass=ABCMeta):
    
    def __init__(self, min_value:int|None=None, max_value:int|None=None):
        self._value:int = None
        self._min:int = min_value
        self._max:int = max_value
        # 최근 연산에서 초과된 양과 부족한 양을 기록한다.
        self.over:int = 0
        self.shortage:int = 0

    def is_below_min(self):
        if self._min is not None:
            return self._value < self._min
        return False

    def is_over_max(self):
        if self._max is not None:
            return self._value > self._max
        return False
        
    def validate(self):
        
        if self.is_below_min():
            self._value = self._min
        
        if self.is_over_max():
            self._value = self._max
        
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value:int):
        # min, max에 따라 value를 제한한다.
        self._value = value
        if self.is_below_min():
            self.shortage = self._min - value
            self._value = self._min
        elif self.is_over_max():
            self.over = value - self._max
            self._value = self._max

    def __str__(self):
        return str(self._value)

class Resource(IntValueObject, metaclass=ABCMeta):
    
    def __init__(self, max_value:int|None=None):
        super().__init__(min_value=0, max_value=max_value)
        
class TableObject(metaclass=ABCMeta):
    """
    테이블 오브젝트 (db 파일의 table로 저장되는 녀석들)
    """

    def __iter__(self):
        rtn = list(self.__dict__.values())
        rtn.pop(0) # ID 제거
        return iter(rtn)

    @classmethod
    def get_table_name(cls):
        """
        테이블명은 클래스명과 동일함
        """
        return cls.__name__

    @property
    def table_name(self):
        return self.__class__.__name__

    @classmethod
    def get_column_set(cls):
        """
        테이블의 컬럼명을 집합으로 반환
        """
        return set(cls.__annotations__.keys())
    
    @property
    def column_set(self):
        return set(self.__class__.__annotations__.keys())

    def get_keys_string(self) -> str:
        """
        sql문에서 컬럼명을 채우기 위한 문자열 반환\n
        ID는 제외함
        """
        keys = list(self.__dict__.keys())
        keys.remove("ID")
        return ", ".join(keys)
    
    @property
    def keys_string(self) -> str:
        keys = list(self.__dict__.keys())
        keys.remove("ID")
        return ", ".join(keys)

    def get_values_string(self) -> str:
        """
        sql문에서 컬럼값을 채우기 위한 문자열 반환\n
        ID는 제외함
        """
        values = list(self.__dict__.values())
        values.pop(0)
        return ", ".join([f"'{value}'" if isinstance(value, str) else str(value) for value in values])
    
    @property
    def values_string(self) -> str:
        values = list(self.__dict__.values())
        values.pop(0)
        return ", ".join([f"'{value}'" if isinstance(value, str) else str(value) for value in values])
    
    def get_wildcard_string(self) -> str:
        """
        sql문에서 ?를 채우기 위한 문자열 반환
        """
        return ", ".join(["?" for i in range(len(self.__dict__) - 1)])
    
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
    @abstractmethod
    def kr_list(self) -> list[str]:
        pass
    
    @property
    def kr_dict(self) -> dict[str, str]:
        # 한국어 : 대응되는 attribute 값
        return dict(zip(self.kr_list, self.__dict__.values()))
    
    @property
    def kr_dict_without_id(self) -> dict[str, str]:
        # 한국어 : 대응되는 attribute 값
        return dict(zip(self.kr_list[1:], list(self.__dict__.values())[1:]))