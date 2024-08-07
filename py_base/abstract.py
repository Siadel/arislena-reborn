import random
from typing import ClassVar
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import IntEnum, Enum

from py_base import jsonwork, yamlwork

class ArislenaEnum(IntEnum):
    """
    Arislena에서 사용하는 Enum의 기본 클래스
    """
    def __new__(cls, *args, **kwds):
        obj = int.__new__(cls)
        obj._value_ = len(cls.__members__)
        return obj
    
    def __init__(self, local_name: str, emoji: str = "", level: int = 0):
        self.local_name: str = local_name
        self.emoji: str = emoji
        self.level: int = level
    
    def __str__(self) -> str:
        return self.name
    
    def __int__(self) -> int:
        return self.value
    
    def __repr__(self) -> str:
        return super().__repr__()

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return self.value == other
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def express(self) -> str:
        """
        이모지, 번역 이름을 반환함
        """
        return f"{self.emoji} {self.local_name}"
    
    def to_discord_text(self) -> str:
        """
        express()와 같지만 local_name 부분을 **로 감싸줌
        """
        return f"{self.emoji} **{self.local_name}**"
    
    @classmethod
    def from_int(cls, value:int) -> "ArislenaEnum":
        return cls(value)


class DetailEnum(IntEnum):
    """
    메타적 디테일을 더해주는 Enum
    """
    
    def __new__(cls, *args, **kwds):
        obj = int.__new__(cls)
        obj._value_ = len(cls.__members__)
        return obj
    
    def __init__(self, corresponding, details:tuple[str]):
        self.corresponding = corresponding
        self.details = details
        
    @classmethod
    def get_from_corresponding(cls, corresponding) -> "DetailEnum":
        if corresponding is None: raise ValueError("None은 사용할 수 없습니다.")
        for detail in cls:
            if detail.corresponding == corresponding:
                return detail
        raise ValueError(f"해당하는 corresponding이 없습니다. {corresponding}")
        
    def get_random_detail_index(self) -> int:
        return random.randint(0, len(self.details) - 1)
        
    def get_detail(self, index: int = None) -> str:
        """
        usage example:
        ```
        Details.COMPONENT.get_detail(random.randint(0, len(Details.<any>.details) - 1))
        ```
        """
        if index is None: index = self.get_random_detail_index()
        return self.details[index]
    
    def get_random_detail(self) -> str:
        return self.get_detail(self.get_random_detail_index())

@dataclass
class JsonObject(metaclass=ABCMeta):
    """
    json 파일과 연동되는 클래스들의 부모 클래스
    """

    file_name: ClassVar[str] = None

    @classmethod
    def from_json(cls, data:dict):
        return cls(**data)
    
    @classmethod
    def from_json_file(cls):
        return cls.from_json(jsonwork.load_json(cls.file_name))
    
    def get(self, key:str, default=None) -> dict | list | str | int | float | None:
        return getattr(self, key, default)
    
    def to_json(self):
        return self.__dict__
    
    def delete_a_key(self, key:str):
        delattr(self, key)
    
    def update_a_key(self, key:str, value):
        setattr(self, key, value)
    
    def dump(self):
        jsonwork.dump_json(self.__dict__, self.__class__.file_name)

@dataclass(init=False)
class FluidJsonObject(JsonObject, metaclass=ABCMeta):

    file_name: ClassVar[str] = None

    @abstractmethod
    def __init__(self, **kwargs):
        """
        . 대신 getattr()로 클래스 변수를 가져오는 것을 권장
        """
        self.__dict__.update(kwargs)

class YamlObject(metaclass=ABCMeta):
    
    file_name: ClassVar[str] = None
    
    def __init__(self) -> None:
        self.data: dict = yamlwork.load_yaml(self.__class__.file_name)

