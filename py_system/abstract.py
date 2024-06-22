import re

from abc import ABCMeta, abstractmethod
from sqlite3 import Row
from typing import Iterable, Iterator, Self

from py_base.ari_enum import get_enum, get_intenum, ResourceCategory, BuildingCategory, Availability
from py_base.utility import sql_type
from py_base.dbmanager import DatabaseManager
from py_base.abstract import ArislenaEnum, DetailEnum
from py_base.yamlobj import TableObjTranslate
from py_base.arislena_dice import Nonahedron

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
        self,
        id:int = 0
    ):
        self.id: int = id
        
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
    def from_data_iter(cls, sqlite_rows:Iterable[Row]) -> Iterator[Self]:
        """
        Creates a list of table objects from the database, using the sqlite3.Row object.

        This function not sets the database attribute of the table object. You should set the database attribute manually.
        """
        return iter(cls.from_data(row) for row in sqlite_rows)
    
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

            annotation = str(type(getattr(self, key))).removeprefix("<").removesuffix(">").split("'")
            ref_class = annotation[0].strip()
            class_name = annotation[1].strip()
            
            if row[key] is None: continue # None 값은 무시 (기본값으로 설정됨)
            
            match (ref_class, class_name):
                
                case (_, "int") | (_, "str") | (_, "float"):
                    setattr(self, key, row[key])
                case (_, "bool"):
                    setattr(self, key, bool(row[key]))
                case (_, "py_base.datatype.ExtInt"):
                    setattr(self, key, getattr(self, key) + row[key])
                case (_, "enum.EnumType"):
                    setattr(self, key, get_enum(class_name, row[key]))
                case ("enum", _):
                    setattr(self, key, get_intenum(class_name, int(row[key])))
                case _:
                    raise ValueError(f"지원하지 않는 데이터 형식입니다: {type(row[key])}, 값: {row[key]}")
        
    def get_dict(self) -> dict:
        """
        self.__dict__를 호출하나 key가 '_'로 시작하는 것은 제외
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def get_dict_without_id(self) -> dict:
        """
        self.__dict__를 호출하나 key가 '_'로 시작하는 것과 id는 제외
        """
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and k != "id"}
    
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

        return sql_type(type(getattr(self, column_name)))
    
    def get_create_table_string(self) -> str:
        """
        Returns the string for table creation in SQL.

        Returns:
            str: The SQL string for creating the table.
        """
        keys = self.get_dict().keys()
        foreign_keys:list[str] = [key for key in keys if re.match(r"\w+_id", key)]
        sub_queries = []

        for key in keys:
            if key == "id":
                sub_queries.append(f"{key} INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                sub_queries.append(f"{key} {self.get_column_type(key)}")

        for foreign_key in foreign_keys:
            sub_queries.append(f"FOREIGN KEY ({foreign_key}) REFERENCES {foreign_key.split('_')[0]}(id)")

        return f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(sub_queries)})"
    
    def pull(self, *raw_statements, **statements):
        """
        Fetches the data from the table which has the same name as the object's class name.

        If the data does not exist, an exception is raised.

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
        
        if not row:
            raise ValueError(f"해당 조건({raw_statements} | {statements})으로 데이터베이스에서 데이터를 찾을 수 없습니다.")

        self._set_attributes_from_sqlite_row(row)
    
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
        
    def to_discord_text(self, translate:TableObjTranslate) -> str:
        """
        Returns the text for the discord message.

        Returns:
            str: The text for the discord message.
        """

        texts = []
        for key, value in self.get_dict().items():
            key = translate.get(key, self.table_name, key)
            if isinstance(value, ArislenaEnum):
                value = value.to_discord_text()
            elif isinstance(value, DetailEnum):
                continue
            else:
                value = f"**{value}**"
            texts.append(f"- {key} : {value}")
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


class Workable(metaclass=ABCMeta):
    """
    노동력을 가지는 객체
    """
    def __init__(self):
        
        self._labor_dice: Nonahedron = None
    
    @property
    def labor_dice(self):
        return self._labor_dice
    
    @abstractmethod
    def get_consumption_recipe(self) -> list[GeneralResource]:
        """
        노동력 소모에 필요한 자원을 반환함
        """
        pass
    
    @abstractmethod
    def set_labor_dice(self):
        """
        experience 수치에 따라 주사위의 modifier가 다르게 설정됨
        """
        self._labor_dice = Nonahedron()
        return self
    
    @abstractmethod
    def set_labor(self):
        return self

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
