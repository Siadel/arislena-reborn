import re

from abc import ABCMeta, abstractmethod
from sqlite3 import Row
from typing import Iterable, Iterator, Self, Any
from enum import IntEnum

from py_base.ari_enum import get_enum, get_intenum, ResourceCategory, BuildingCategory, Availability
from py_base.ari_logger import ari_logger
from py_base.datatype import ExtInt
from py_base.utility import sql_type
from py_base.dbmanager import DatabaseManager
from py_base.abstract import ArislenaEnum, DetailEnum
from py_base.yamlobj import TableObjTranslator

class Column:
    
    def __init__(
        self,
        annotation: type,
        *,
        show_front: bool = True,
        primary_key: bool = False,
        auto_increment: bool = False,
        not_null: bool = True,
        unique: bool = False
    ):
        """
        name : name of the column
        annotation : type of the column
        value : value of the column
        show_front : whether to display the column in the front(discord)
        primary_key : whether the column is a primary key
        auto_increment : whether the column is auto increment
        not_null : whether the column is not null
        unique : whether the column is unique
        """
        self._name: str = None
        self._value: annotation = None
        self.annotation = annotation
        self.show_front = show_front
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.not_null = not_null
        self.unique = unique
        
    def __str__(self):
        return str(self._value)
    
    def __get__(self, instance, owner):
        if instance is None: return self
        # print(f"Column {self._name} is accessed; {instance} {owner}")
        return instance.__dict__[self._name]
    
    def __set__(self, instance: object, value):
        # print(f"Column {self._name} will set; {instance} with value {value}, which type is {type(value)}")
        if not isinstance(value, self.annotation):
            raise TypeError(f"(function skipped) Column {self._name} is not {self.annotation} type. The value is '{value}' ({type(value)}).")
            
        instance.__dict__[self._name] = value
        
    def __set_name__(self, owner, name):
        self._name = name
    
    def __delete__(self, instance):
        del self._value
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def sql_type(self) -> str:
        """
        Returns the data type of the column used in SQL.
        """
        if self.annotation.__module__ == "builtins":
            match self.annotation.__name__:
                case "str": return "TEXT"
                case "int": return "INTEGER"
                case "float": return "REAL"
                case "NoneType": return "NULL"
                case "bool": return "INTEGER"
        elif self.annotation is ExtInt: return "INTEGER"
        elif issubclass(self.annotation, IntEnum): return "INTEGER"
        
        else: raise ValueError(f"Type {self.annotation} is not supported in Arislena's SQL.")
        
    @property
    def creator(self) -> str:
        """
        Returns the string for column creation in SQL.

        Returns:
            str: The SQL string for creating the column.
        """
        sub_queries = []
        sub_queries.append(f"{self._name} {self.sql_type}")
        if self.primary_key: sub_queries.append("PRIMARY KEY")
        if self.auto_increment: sub_queries.append("AUTOINCREMENT")
        if self.not_null: sub_queries.append("NOT NULL")
        if self.unique: sub_queries.append("UNIQUE")
        return " ".join(sub_queries)

    @property
    def foreign_key_creator(self):
        """
        Returns the string for foreign key creation in SQL.

        Returns:
            str: The SQL string for creating the foreign key.
        """
        if self.is_foreign_key():
            return f"FOREIGN KEY ({self._name}) REFERENCES {self._name.split('_')[0]}(id)"
        else:
            return ""
    
    def is_foreign_key(self) -> bool:
        return self._name.endswith("_id")

class TableObject(metaclass=ABCMeta):
    """
    Initialize the table object.

    Args:
        `id (int, optional)`: The ID of the table object. Defaults to 0.
    
    Private Attributes:
        `_database (DatabaseManager)`: The main database, which is the only database that the table object and its children can access.
    
    Properties:
        `kr_list (list[str])`: A list of Korean names of the attributes.
        `__dict__ (dict[str, Any])`: A dictionary containing the values of all attributes defined in the __columns__ list.
        `table_name (str)`: The name of the table in the database.
        `column_set (set[str])`: A set of attribute names.
        `en_kr_dict (dict[str, str])`: A dictionary that maps the attribute names to their Korean names.
        `kr_dict (dict[str, str])`: A dictionary that maps the Korean names to the attribute values.
        `kr_dict_without_id (dict[str, str])`: A dictionary that maps the Korean names to the attribute values, excluding the 'id' attribute.
        `database (DatabaseManager)`: The main database, which is the only database that the table object and its children can access.
    """
    
    abstract = True # TableObject 클래스를 상속하지만 추상 클래스로 사용할 경우 True로 설정
    
    def __init__(
        self
    ):  
        self.id: int
        self._database: DatabaseManager = None
    
    @abstractmethod
    def get_display_string(self) -> str:
        """
        이 클래스의 지정된 column 값을 반환
        """
        pass
    
    def set_database(self, database:DatabaseManager):
        self._database = database
        return self
    
    @classmethod
    def get_table_name(cls) -> str:
        """
        이 클래스의 테이블 이름을 반환
        """
        return cls.__name__
    
    @classmethod
    def fetch_or_raise(cls, database:DatabaseManager, _raise: Exception, *raw_statements, **statements):
        """
        데이터베이스에서 데이터를 가져오거나, 데이터가 없을 경우 예외를 발생시킵니다.
        """
        data = database.fetch(cls.get_table_name(), *raw_statements, **statements)
        if data is None:
            raise _raise
        return cls.from_data(data)
    
    @classmethod
    def from_database(cls, database:DatabaseManager, *raw_statements, **statements):
        """
        Creates a table object from the database.

        Also sets the database attribute of the table object.
        """
        new_obj = cls()
        new_obj.set_database(database)
        if raw_statements or statements:
            new_obj.pull(*raw_statements, **statements)
        return new_obj
    
    @classmethod
    def from_data(cls, sqlite_row:Row | None, **kwargs) -> Self:
        """
        Creates a table object from the database, using the sqlite3.Row object.

        This function not sets the database attribute of the table object. You should set the database attribute manually.
        
        if sqlite_row is None, returns object with default values.
        
        You can also pass the keyword arguments to set the attributes of the object, if the sqlite_row is None.
        """

        # if not set(sqlite_row.keys()).issubset(cls.__annotations__.keys()):
        #     raise ValueError(f"데이터베이스의 컬럼과 클래스의 어노테이션에 불일치가 있습니다: {set(sqlite_row.keys()) - set(cls.__annotations__.keys())}")
        if sqlite_row is not None:
            new_cls = cls()
            new_cls._set_attributes_from_sqlite_row(sqlite_row)
            return new_cls
        else:
            return cls(**kwargs)
    
    @classmethod
    def from_data_iter(cls, sqlite_rows:Iterable[Row], database: DatabaseManager = None) -> Iterator[Self]:
        """
        Creates a list of table objects from the database, using the sqlite3.Row object.
        """
        if database:
            return iter(cls.from_data(row).set_database(database) for row in sqlite_rows)
        return iter(cls.from_data(row) for row in sqlite_rows)
        
    @classmethod
    def from_database_to_iter(cls, database:DatabaseManager, *raw_statements, **statements):
        """
        Creates a list of table objects from the database.
        """
        rows = database.fetch_many(cls.get_table_name(), *raw_statements, **statements)
        return cls.from_data_iter(rows, database)
    
    @property
    def table_name(self):
        return self.__class__.get_table_name()
    
    @property
    def database(self) -> DatabaseManager:
        return self._database
    
    def _check_database(self):
        if self._database is None:
            raise Exception("Database is not set.")
    
        
    def _set_attributes_from_sqlite_row(self, row:Row):
        """
        Sets the attributes of the table object from the sqlite3.Row object.
        """

        for key in row.keys():
            
            _get = getattr(self.__class__, key, None)
            if not isinstance(_get, Column): continue
            
            if _get.annotation.__module__ == "builtins":
                match _get.annotation.__name__:
                    case "str" | "int" | "float": setattr(self, key, row[key])
                    case "bool": setattr(self, key, bool(row[key]))
                    case "NoneType": setattr(self, key, None)
            elif _get.annotation is ExtInt: setattr(self, key, getattr(self, key) + row[key])
            elif issubclass(_get.annotation, IntEnum): setattr(self, key, get_intenum(_get.annotation.__name__, row[key]))
            else: raise ValueError(f"Type {_get.annotation} is not supported in Arislena's SQL.")
    
    def set_value(self, key:str, value:Any):
        """
        key가 Column 객체인 경우 해당 key의 value 설정
        """
        _get = getattr(self.__class__, key, None)
        if isinstance(_get, Column) and isinstance(value, _get.annotation):
            _get._value = value
            
    @classmethod
    def get_columns(cls) -> dict[str, Column]:
        """
        Returns the dictionary of the columns.
        """
        return {k: v for k, v in cls.__dict__.items() if isinstance(v, Column)}
    
    @classmethod
    def get_showables(cls) -> list[str]:
        """
        Returns the list of the attributes that are shown in the front-end.
        """
        return [k for k, v in cls.__dict__.items() if isinstance(v, Column) and v.show_front]
        
    def get_dict(self) -> dict[str, Any]:
        """
        self.__dict__를 호출하나 _로 시작하는 attribute는 제외
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def get_dict_without_id(self) -> dict[str, Any]:
        """
        self.__dict__를 호출하나 _로 시작하는 attribute와 id는 제외
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_") and k != "id"}
    
    def get_wildcard_string(self) -> str:
        """
        sql문에서 ?를 채우기 위한 문자열 반환

        id를 제외한 모든 attribute 값을 ?로 반환
        """
        return ", ".join(["?" for _ in range(len(self.get_dict_without_id()))])
    
    def get_column_type(self, column_name: str) -> str:
        """
        Returns the data type of the column used in SQL.

        Args:
            column_name (str): The name of the column.

        Returns:
            str: The data type of the column in SQL.

        Raises:
            Exception: If the data type is not supported in SQL.

        """

        _get = getattr(self.__class__, column_name, None)
        if isinstance(_get, Column):
            return _get.sql_type
        else:
            raise ValueError(f"Column {column_name} is not found.")
    
    @classmethod
    def get_create_table_string(cls) -> str:
        """
        Returns the string for table creation in SQL.

        Returns:
            str: The SQL string for creating the table.
        """
        sub_queries = []
        foreign_keys = []

        for v in cls.get_columns().values():
            sub_queries.append(v.creator)
            if v.is_foreign_key():
                foreign_keys.append(v.foreign_key_creator)
        
        if foreign_keys:
            sub_queries.extend(foreign_keys)

        return f"CREATE TABLE IF NOT EXISTS {cls.get_table_name()} ({', '.join(sub_queries)})"
    
    def pull(self, *raw_statements, **statements):
        """
        Fetches the data from the table which has the same name as the object's class name.

        If the data does not exist, this function sets the object's attributes to the values passed as arguments. (only for KWARGS statements)

        If the data exists, it will update the object's attributes.

        Args:
            raw_statements (tuple[str]): The raw SQL statements.
            statements (dict[str, Any]): The key-value pairs of the SQL statements.
        
        Raises:
            Exception: If the database is not set.
            Exception: If the data is not fetched from the database successfully.
        """
        self._check_database()
        
        row = self._database.fetch(self.table_name, *raw_statements, **statements)
        
        if row:
            self._set_attributes_from_sqlite_row(row)
        else:
            for k, v in statements.items():
                setattr(self, k, v)
    
    def push(self):
        """
        Pushes the data to the table which has the same name as the object's class name.

        If the data does not exist, it will insert the data.

        If the data exists, it will update the data.

        Raises:
            Exception: If the database is not set.
        """
        self._check_database()
        if self._database.is_exist(self.table_name, f"id = {self.id}"):
            self._database.update_with_id(self.table_name, self.id, **self.get_dict_without_id())
        else:
            data = self.get_dict_without_id()
            self._database.insert(self.table_name, data.keys(), data.values())
            
    def update(self, **kwargs):
        """
        Updates the data to the table which has the same name as the object's class name.

        Args:
            kwargs (dict[str, Any]): The key-value pairs of the SQL statements.

        Raises:
            Exception: If the database is not set.
        """
        self._check_database()
        self.__setattr__(**kwargs)
        self._database.update_with_id(self.table_name, self.id, **kwargs)
    
    def delete(self):
        """
        Deletes the data from the table which has the same name as the object's class name.

        Raises:
            Exception: If the database is not set.
        """
        self._check_database()
        self._database.delete_with_id(self.table_name, self.id)
        
    def to_embed_value(self, translator:TableObjTranslator) -> str:
        """
        Returns the text for the discord embed.

        Returns:
            str: The text for the discord embed.
        """

        texts = []
        discord_text = ""
        for key in self.get_showables():
            value = getattr(self, key)
            show_key = translator.get(key, self.table_name, key)
            if isinstance(value, ArislenaEnum):
                discord_text = value.to_discord_text()
            elif isinstance(value, DetailEnum):
                continue
            else:
                discord_text = f"**{value}**"
            texts.append(f"- {show_key} : {discord_text}")
        return "\n".join(texts)

class ResourceAbst(metaclass=ABCMeta):
    
    def __init__(self, category:ResourceCategory, amount:int):
        self.category = category
        self.amount = amount

    def __str__(self):
        return self.category.name
    
    def __int__(self):
        return int(self.amount)
    
    def _check_category(self, other:"ResourceAbst"):
        """
        같은 카테고리인지 확인
        """
        if not isinstance(other, ResourceAbst): raise TypeError(f"{ResourceAbst.__name__} 객체가 아닙니다.")
        if self.category != other.category: raise ValueError("카테고리가 다릅니다.")

    def move(self, other:"ResourceAbst", *, amount:int = None):
        """
        다른 자원 객체로 자원을 이동
        """
        self._check_category(other)
        if amount is None or amount > self.amount: amount = self.amount
        
        other.amount += amount
        self.amount -= amount    
    
    def __add__(self, other:"ResourceAbst"):
        self._check_category(other)
        return ResourceAbst(self.category, self.amount + other.amount)
    
    def __sub__(self, other:"ResourceAbst"):
        self._check_category(other)
        return ResourceAbst(self.category, self.amount - other.amount)
    
    # 카테고리가 다른 경우 amount 값과 상관 없이 False 반환
    
    def __lt__(self, other:"ResourceAbst"):
        return self.category == other.category and self.amount < other.amount
    
    def __le__(self, other:"ResourceAbst"):
        return self.category == other.category and self.amount <= other.amount
    
    def __eq__(self, other:"ResourceAbst"):
        return self.category == other.category and self.amount == other.amount
    
    def __ne__(self, other:"ResourceAbst"):
        return self.category == other.category and self.amount != other.amount
    
    def __gt__(self, other:"ResourceAbst"):
        return self.category == other.category and self.amount > other.amount
    
    def __ge__(self, other:"ResourceAbst"):
        return self.category == other.category and self.amount >= other.amount


class BuildingAbst(metaclass=ABCMeta):
    
    def __init__(
        self, 
        category:BuildingCategory, 
        level:int
    ):
        self.category = category
        self.level = level

class GeneralResource(ResourceAbst):
    
    def __init__(
        self, 
        category: ResourceCategory, 
        amount: int = 1
    ):
        super().__init__(category, amount)


# deprecated
# @dataclass
# class Storages(Buildings, metaclass=ABCMeta):
#     """
#     창고 클래스들의 부모 클래스
#     """
#     category: int = None
#     level: int = 0
#     storages: list[ResourceBase] = field(default_factory=list)

#     def level_up(self):
#         self.level += 1
#         for storage in self.storages:
#             storage.amount += (storage.amount // 20) * 10
    
#     @property
#     def level_up_cost(self):
#         """
#         level 당 건자재 2, 주사위 총량 10 필요
#         return : dict
#         return format : {
#             "building_material" : 건자재,
#             "dice_cost" : 주사위 총량
#         }
#         """
#         return {
#             "building_material" : 10 * self.level,
#             "dict_cost" : 10 * self.level
#         }
