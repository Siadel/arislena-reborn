from typing import ClassVar
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import IntEnum, Enum

from py_base import jsonwork

class ArislenaEnum(IntEnum):
    """
    Arislena에서 사용하는 Enum의 기본 클래스
    """
    def __new__(cls, *args, **kwds):
        obj = int.__new__(cls)
        obj._value_ = len(cls.__members__)
        return obj
    
    def __init__(self, local_name:str, emoji:str):
        self.local_name:str = local_name
        self.emoji:str = emoji
    
    def __str__(self) -> str:
        return self.name
    
    def __int__(self) -> int:
        return self.value
    
    def __repr__(self) -> str:
        return super().__repr__()
    
    @classmethod
    def from_int(cls, value:int) -> "ArislenaEnum":
        return cls(value)

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




