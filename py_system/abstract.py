import re
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from py_base import jsonwork
from py_base.utility import sql_value
from py_base.dbmanager import MainDB



class TableObject(metaclass=ABCMeta):
    
    __columns__: tuple = ("ID",)

    def __init__(self, id:int = 0):
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
            `items (dict[str, Any])`: A dictionary containing the values of all attributes defined in the __columns__ list.
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
        self.id = id
        self.display_column = None
        self._database = None

    def __str__(self):
        return f"{self.__class__.__name__}({self.items})"

    def __iter__(self):
        rtn = list(self.items.values())
        rtn.pop(0) # ID 제거
        return iter(rtn)
    
    @property
    @abstractmethod
    def kr_list(self) -> list[str]:
        return ["아이디"]
    
    @property
    def items(self):
        """
        Returns a dictionary containing the values of all attributes defined in the `__columns__`.

        The keys of the dictionary are the attribute names.
        """
        return {column : self.__getattribute__(column) for column in self.__columns__}
    
    @property
    def table_name(self):
        return self.__class__.__name__
    
    @property
    def column_set(self):
        return set(self.__columns__)
        
    @property
    def en_kr_dict(self) -> dict[str, str]:
        # 영어 : 한국어
        return dict(zip(self.__columns__, self.kr_list))
    
    @property
    def kr_dict(self) -> dict[str, str]:
        # 한국어 : 대응되는 attribute 값
        return dict(zip(self.kr_list, self.items.values()))
    
    @property
    def kr_dict_without_id(self) -> dict[str, str]:
        # 한국어 : 대응되는 attribute 값
        return dict(zip(self.kr_list[1:], list(self.items.values())[1:]))
    
    @property
    def database(self):
        return self._database
    
    @database.setter
    def database(self, database:MainDB):
        self._database = database
        
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
        for key, value in self.items.items():
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
        return ", ".join(["?" for _ in range(len(self.__columns__) - 1)])
    
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
        dtype_dict = {
            "str": "TEXT",
            "int": "INTEGER",
            "float": "REAL",
            "NoneType": "NULL",
            "extint": "INTEGER"
        }
        value = type(self.items[column_name]).__name__
        anno = str(value).lower()
        if anno in dtype_dict:
            return dtype_dict[anno]
        else:
            raise Exception("The data type is not supported in SQL. Please use 'str', 'int', or 'float'.")
    
    def get_create_table_string(self) -> str:
        """
        Returns the string for table creation in SQL.

        Returns:
            str: The SQL string for creating the table.
        """
        foreign_keys:list[str] = [key for key in self.__columns__ if re.match(r"\w+_id", key)]
        sub_queries = []

        for key in self.__columns__:
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
            raise Exception("Fetch from database failed: Found no data.")

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
            self._database.update_with_id(self.table_name, self.id, **self.items)
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