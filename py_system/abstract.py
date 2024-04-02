import re

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar
from sqlite3 import Row

from py_base.ari_enum import get_enum, ResourceCategory, BuildingCategory
from py_base.utility import sql_type
from py_base.dbmanager import MainDB

@dataclass
class TableObject(metaclass=ABCMeta):
    """
    Initialize the table object.

    Args:
        `id (int, optional)`: The ID of the table object. Defaults to 0.

    Class Attributes:
        `__columns__ (tuple)`: A tuple containing the names of all attributes in the table object. It must be defined manually in the child class.
    
    Private Attributes:
        `_database (MainDB)`: The main database, which is the only database that the table object and its children can access.
    
    Properties:
        `kr_list (list[str])`: A list of Korean names of the attributes.
        `__dict__ (dict[str, Any])`: A dictionary containing the values of all attributes defined in the __columns__ list.
        `table_name (str)`: The name of the table in the database.
        `column_set (set[str])`: A set of attribute names.
        `en_kr_dict (dict[str, str])`: A dictionary that maps the attribute names to their Korean names.
        `kr_dict (dict[str, str])`: A dictionary that maps the Korean names to the attribute values.
        `kr_dict_without_id (dict[str, str])`: A dictionary that maps the Korean names to the attribute values, excluding the 'id' attribute.
        `database (MainDB)`: The main database, which is the only database that the table object and its children can access.
    
    Examples:
        Option 1: set the database attribute after creating the object + call the pull method
    ```python
    # External database connection is required.
    from py_system.global_ import main_db
    faction = Faction()
    faction.set_database(main_db)
    faction.pull("id = 1")
    print(faction)
    # modify the attributes
    faction.name = "Survivors"
    # push the data to the database
    faction.push()
    ```
        Option 2: use kwargs to set the attributes, without setting the database attribute and calling the pull method
    ```python
    # External database connection is required.
    from py_system.global_ import main_db
    faction = Faction.from_data(main_db.fetch("faction", "id = 1"))
    # also:
    faction = Faction.from_database(main_db, id=1)
    print(faction)
    # set database
    faction.set_database(main_db)
    # modify the attributes
    faction.name = "Survivors"
    # push the data to the database
    faction.push()
    ```
    """
    id: int = 0

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = None
    en_kr_map: ClassVar[dict[str, str]] = None

    def __iter__(self):
        rtn = list(self.__dict__.values())
        rtn.pop(0) # ID 제거
        return iter(rtn)
    
    @abstractmethod
    def display(self) -> str:
        """
        이 클래스의 지정된 column 값을 반환
        """
        pass
    
    def _set_attributes_from_sqlite_row(self, row:Row):
        """
        Sets the attributes of the table object from the sqlite3.Row object.
        """

        for key in row.keys():

            annotation = str(self.__class__.__annotations__[key]).removeprefix("<").removesuffix(">").split("'")
            ref_instance = annotation[0].strip()
            class_name = annotation[1].strip()
            
            if row[key] is None: continue # None 값은 무시 (기본값으로 설정됨)

            match (class_name, ref_instance):

                case ("int", _) | ("str", _) | ("float", _):
                    setattr(self, key, row[key])
                case ("ExtInt", _):
                    setattr(self, key, self.__getattribute__(key) + row[key])
                case (_, "enum"):
                    setattr(self, key, get_enum(class_name, row[key]))
                case _:
                    raise ValueError(f"지원하지 않는 데이터 형식입니다: {str(self.__annotations__[key])}, 값: {row[key]}")
    
    @classmethod
    def set_database(cls, database:MainDB):
        cls._database = database
    
    @classmethod
    def from_database(cls, database:MainDB, *raw_statements, **statements):
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
    def from_data(cls, sqlite_row:Row):
        """
        Creates a table object from the database, using the sqlite3.Row object.

        This function not sets the database attribute of the table object. You should set the database attribute manually.
        """

        new_obj = cls()

        if not set(sqlite_row.keys()).issubset(set(cls.__annotations__.keys())):
            raise ValueError(f"데이터베이스의 컬럼과 클래스의 어노테이션에 불일치가 있습니다: {set(sqlite_row.keys()) - set(cls.__annotations__.keys())}")

        new_obj._set_attributes_from_sqlite_row(sqlite_row)
            
        return new_obj
    
    @property
    def table_name(self):
        return self.__class__.__name__
    
    @property
    def database(self) -> MainDB:
        return self._database
    
    def _check_database(self):
        if not self._database:
            raise Exception("Database is not set.")
    
    def get_column_names(self) -> list[str]:
        columns = list(self.__dict__.keys())
        columns.remove("id")
        return columns
    
    def get_data_tuple(self) -> tuple:
        datas = list(self.__dict__.values())
        datas.pop(0)
        return tuple(datas)
    
    def get_wildcard_string(self) -> str:
        """
        sql문에서 ?를 채우기 위한 문자열 반환

        id를 제외한 모든 attribute 값을 ?로 반환
        """
        return ", ".join(["?" for _ in range(len(self.__dict__.keys()) - 1)])
    
    def get_column_type(self, column_name: str) -> str:
        """
        Returns the data type of the column used in SQL.

        Args:
            column_name (str): The name of the column.

        Returns:
            str: The data type of the column in SQL.

        Raises:
            Exception: If the data type is not supported in SQL (only supports 'str', 'int', 'float').

        """

        return sql_type(getattr(self, column_name))
    
    def get_create_table_string(self) -> str:
        """
        Returns the string for table creation in SQL.

        Returns:
            str: The SQL string for creating the table.
        """
        foreign_keys:list[str] = [key for key in self.__dict__.keys() if re.match(r"\w+_id", key)]
        sub_queries = []

        for key in self.__dict__.keys():
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
            self._database.update_with_id(self.table_name, self.id, **self.__dict__)
        else:
            self._database.insert(self.table_name, self.get_column_names(), self.get_data_tuple())
    
    def delete(self):
        """
        Deletes the data from the table which has the same name as the object's class name.

        Raises:
            Exception: If the database is not set.
        """
        self._check_database()
        self._database.delete_with_id(self.table_name, self.id)

class ResourceBase(metaclass=ABCMeta):
    
    def __init__(self, category:ResourceCategory, amount:int):
        self.category = category
        self.amount = amount

    def __str__(self):
        return self.category.name
    
    def __int__(self):
        return int(self.amount)
    
    def _check_category(self, other:"ResourceBase"):
        """
        같은 카테고리인지 확인
        """
        if not isinstance(other, ResourceBase): raise TypeError("ResourceBase 객체가 아닙니다.")
        if self.category != other.category: raise ValueError("카테고리가 다릅니다.")

    def move(self, other:"ResourceBase", *, amount:int = None):
        """
        다른 자원 객체로 자원을 이동
        """
        self._check_category(other)
        if amount is None or amount > self.amount: amount = self.amount
        
        other.amount += amount
        self.amount -= amount
        
    def __add__(self, other:"ResourceBase"):
        self._check_category(other)
        return ResourceBase(self.category, self.amount + other.amount)
    
    def __sub__(self, other:"ResourceBase"):
        self._check_category(other)
        return ResourceBase(self.category, self.amount - other.amount)
    
    def __lt__(self, other:"ResourceBase"):
        return self.category == other.category and self.amount < other.amount
    
    def __le__(self, other:"ResourceBase"):
        return self.category == other.category and self.amount <= other.amount
    
    def __eq__(self, other:"ResourceBase"):
        return self.category == other.category and self.amount == other.amount
    
    def __ne__(self, other:"ResourceBase"):
        return self.category == other.category and self.amount != other.amount
    
    def __gt__(self, other:"ResourceBase"):
        return self.category == other.category and self.amount > other.amount
    
    def __ge__(self, other:"ResourceBase"):
        return self.category == other.category and self.amount >= other.amount
        

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
