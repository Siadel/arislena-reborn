import re
from typing import ClassVar
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from py_base import jsonwork
from py_base.utility import sql_value
from py_base.dbmanager import MainDB

class JsonObject(metaclass=ABCMeta):
    """
    json 파일과 연동되는 클래스들의 부모 클래스
    """

    @classmethod
    def from_json(cls, data:dict):
        return cls(**data)
    
    def get(self, key:str):
        return getattr(self, key)
    
    def to_json(self):
        return self.__dict__
    
    def delete_a_key(self, key:str):
        delattr(self, key)
    
    def update_a_key(self, key:str, value):
        setattr(self, key, value)

class FluidJsonObject(JsonObject, metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

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
    faction.database = main_db
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
    faction = Faction(**main_db.fetch("faction", "id = 1"))
    print(faction)
    # set database
    faction.database = main_db
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
        new_obj._database = database
        if raw_statements or statements:
            new_obj.pull(*raw_statements, **statements)
        return new_obj
    
    @property
    def table_name(self):
        return self.__class__.__name__
    
    @property
    def column_set(self):
        return set(self.__dict__.keys())
    
    @property
    def kr_dict(self) -> dict[str, str]:
        # 한국어 : 대응되는 attribute 값
        return dict(zip(self.en_kr_map.values(), self.__dict__.values()))
        
    def get_insert_pair(self) -> tuple[str]:
        """
        Returns the names of all attributes in SQL format, excluding the 'id' attribute.

        :return: A tuple containing a string of attribute names separated by commas and a string of corresponding attribute values separated by commas.
        :rtype: tuple[str]

        :example:
        ```python
        keys_string, values_string = tableobj.get_insert_pair()
        sql = f"INSERT INTO {tableobj.table_name} ({keys_string}) VALUES ({values_string})"
        ```
        """
        keys = []
        values = []
        for key, value in self.__dict__.items():
            if key == "id":
                continue
            keys.append(key)
            values.append(sql_value(value))
        return ", ".join(keys), ", ".join(values)
    
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

        return sql_value(getattr(self, column_name))
    
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
        if not self._database:
            raise Exception("Database is not set.")
        
        row = self._database.fetch(self.table_name, *raw_statements, **statements)
        
        if not row:
            raise Exception("해당 조건으로 데이터베이스에서 데이터를 찾을 수 없습니다.")

        for key in row.keys():
            setattr(self, key, row[key])
    
    def push(self):
        """
        Pushes the data to the table which has the same name as the object's class name.

        If the data does not exist, it will insert the data.

        If the data exists, it will update the data.

        Raises:
            Exception: If the database is not set.
        """
        if not self._database: raise Exception("Database is not set.")
        if self._database.is_exist(self.table_name, f"id = {self.id}"):
            self._database.update_with_id(self.table_name, self.id, **self.__dict__)
        else:
            keys_string, values_string = self.get_insert_pair()
            self._database.insert(self.table_name, keys_string, values_string)
    
    def delete(self):
        """
        Deletes the data from the table which has the same name as the object's class name.

        Raises:
            Exception: If the database is not set.
        """
        if not self._database: raise Exception("Database is not set.")
        self._database.delete_with_id(self.table_name, self.id)

@dataclass
class Buildings(metaclass=ABCMeta):
    """
    시설 클래스들의 부모 클래스
    """
    discriminator: int = None
    name: str = None
    dice_cost: int = None
    level: int = 0
    consumptions: list = field(default_factory=list)
    productions: list = field(default_factory=list)


class Resource(metaclass=ABCMeta):
    
    def __init__(self, name:str, amount:int):
        self.name = name
        self.amount = amount

    def __str__(self):
        return str(self.name)
    
    def __int__(self):
        return int(self.amount)

@dataclass
class Storages(Buildings, metaclass=ABCMeta):
    """
    창고 클래스들의 부모 클래스
    """
    discriminator: int = None
    name: str = None
    level: int = 0
    storages: list[Resource] = field(default_factory=list)

    def level_up(self):
        self.level += 1
        for storage in self.storages:
            storage.amount += (storage.amount // 20) * 10
    
    @property
    def level_up_cost(self):
        """
        level 당 건자재 2, 주사위 총량 10 필요
        return : dict
        return format : {
            "building_material" : 건자재,
            "dice_cost" : 주사위 총량
        }
        """
        return {
            "building_material" : 10 * self.level,
            "dict_cost" : 10 * self.level
        }