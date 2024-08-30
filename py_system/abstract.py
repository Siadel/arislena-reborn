
from abc import ABCMeta, abstractmethod
from sqlite3 import Row
from typing import Iterable, Iterator, Self, Any
from enum import IntEnum
from math import sqrt

from py_base.ari_enum import get_intenum, ResourceCategory, ExperienceCategory
from py_base.datatype import ExtInt, AbsentValue
from py_base.dbmanager import DatabaseManager
from py_base.abstract import ArislenaEnum, DetailEnum
from py_base.yamlobj import TableObjTranslator, ConcreteObjectDescription
from py_base.utility import sql_value
from py_base.arislena_dice import D20

class Column:
    
    def __init__(
        self,
        annotation: type,
        *,
        show_front: bool = True,
        primary_key: bool = False,
        auto_increment: bool = False,
        not_null: bool = False,
        unique: bool = False,
        default: Any = None,
        referenced_table: str = "",
        referenced_column: str = "",
        foreign_key_options: list[str] = []
    ):
        """
        name : name of the column
        annotation : type of the column
        
        default : default value of the column (must be the same type as the annotation)
        show_front : whether to display the column in the front(discord)
        primary_key : whether the column is a primary key
        auto_increment : whether the column is auto increment
        not_null : whether the column is not null
        unique : whether the column is unique
        referenced_table : the table that the column references (foreign key)
        referenced_column : the column that the column references (foreign key)
        foreign_key_options : options for the foreign key
        
        ex) foregn_key_options = ["ON DELETE CASCADE", "ON UPDATE CASCADE"]
        """
        self._name: str = ""
        self._value: annotation | AbsentValue | None = None
        # _value를 Column 외부에서 활용하면 예상치 못한 결과(보통 알 수 없는 에러)를 초래할 수 있음
        self.annotation = annotation
        
        self.show_front = show_front
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.not_null = not_null
        self.unique = unique
        self.default = default
        self.referenced_table = referenced_table
        self.referenced_column = referenced_column
        self.foreign_key_options = foreign_key_options
        
        self.whitelist = self._get_whitelist()
        if default is not None and not isinstance(default, self.annotation):
            raise TypeError(f"Column {self._name} is not {self.annotation} type. The default value is '{default}' ({type(default)}).")
        
    def _get_whitelist(self) -> tuple[type]:
        whitelist = [self.annotation, AbsentValue]
        if not self.not_null: whitelist.append(type(None))
        return tuple(whitelist)
        
    def __str__(self):
        return str(self._value)
    
    def __get__(self, instance: object, owner):
        if instance is None: return self
        # print(f"Column {self._name} is accessed; {instance} {owner}")
        return instance.__dict__[self._name]
    
    def __set__(self, instance: object, value):
        # print(f"Column {self._name} will set; {instance} with value {value}, which type is {type(value)}")
        if not isinstance(value, self.whitelist):
            raise TypeError(f"Column {self._name} is not {self.annotation} type. The value is '{value}' ({type(value)}).")
            
        instance.__dict__[self._name] = value
        
    def __set_name__(self, owner, name):
        self._name = name
    
    def __delete__(self, instance):
        del self._value
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def sql_type(self) -> str | None:
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
        if self.default is not None: sub_queries.append(f"DEFAULT {sql_value(self.default)}")
        
        return " ".join(sub_queries)
    
    @property
    def foreign_key_creator(self) -> str:
        """
        Returns the string for foreign key creation in SQL.

        Returns:
            str: The SQL string for creating the foreign key.
        """
        if not (self.referenced_table and self.referenced_column and self.foreign_key_options): return ""
        creator = f"FOREIGN KEY ({self._name}) REFERENCES {self.referenced_table} ({self.referenced_column})"
        if self.foreign_key_options: creator += " " + " ".join(self.foreign_key_options)
        return creator
    
    def from_sqlite_row(self, row:Row):
        """
        Sets the value of the column from the sqlite3.Row object.
        """
        self._value = row[self._name]

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
    
    table_name: str = ""
    id = Column(int, primary_key=True, auto_increment=True)
    
    def __init__(
        self
    ):  
        self.id = 0
        self._database: DatabaseManager | None = None
        
    @property
    def database(self) -> DatabaseManager:
        return self._database
    
    @abstractmethod
    def get_display_string(self) -> str:
        """
        이 클래스의 지정된 column 값을 반환
        """
        pass
    
    def set_database(self, database:DatabaseManager):
        self._database = database
        return self
    
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
    
    @classmethod
    def fetch_or_raise(cls, database:DatabaseManager, _raise: Exception, *raw_statements, **statements):
        """
        데이터베이스에서 데이터를 가져오거나, 데이터가 없을 경우 예외를 발생시킵니다.
        """
        data = database.fetch(cls.table_name, *raw_statements, **statements)
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
    def from_data_iter(cls, sqlite_rows:Iterable[Row], database: DatabaseManager) -> Iterator[Self]:
        """
        Creates a list of table objects from the database, using the sqlite3.Row object.
        """
        return iter(cls.from_data(row).set_database(database) for row in sqlite_rows)
        
    @classmethod
    def from_database_to_iter(cls, database:DatabaseManager, *raw_statements, **statements):
        """
        Creates a list of table objects from the database.
        """
        rows = database.fetch_many(cls.table_name, *raw_statements, **statements)
        return cls.from_data_iter(rows, database)
            
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
    
    @classmethod
    def get_create_table_query(cls) -> str:
        """
        Returns the string for table creation in SQL.

        Returns:
            str: The SQL string for creating the table.
        """
        sub_queries: list[str] = []
        foreign_keys: list[Column] = []

        for v in cls.get_columns().values():
            sub_queries.append(v.creator)
            if v.referenced_table: foreign_keys.append(v)
        
        if foreign_keys:
            for foreign_key in foreign_keys:
                sub_queries.append(foreign_key.foreign_key_creator)

        return f"CREATE TABLE IF NOT EXISTS {cls.table_name} ({', '.join(sub_queries)})"
    
    def get_insert_information(self) -> dict[str, str]:
        """
        Returns the string for inserting the table in SQL.

        Returns:
            str: The SQL string for inserting the table.
        """
        target_columns = []
        values = []
        for key, column in self.get_columns().items():
            if column.auto_increment: continue
            if column.primary_key: continue
            if isinstance(getattr(self, column.name), AbsentValue): continue
            target_columns.append(key)
            values.append(sql_value(getattr(self, column.name)))
        if not target_columns: return f"INSERT INTO {self.table_name} DEFAULT VALUES"
        return {
            "keys_iter": ", ".join(target_columns),
            "values_iter": ", ".join(values)
        }
    
    def get_update_query(self) -> str:
        """
        Returns the string for updating the table in SQL.

        Returns:
            str: The SQL string for updating the table.
        """
        sub_queries = []
        for key, column in self.get_columns().items():
            if column.primary_key: continue
            if isinstance(getattr(self, column.name), AbsentValue): continue
            sub_queries.append(f"{key} = {sql_value(getattr(self, column.name))}")
        return f"UPDATE {self.table_name} SET {', '.join(sub_queries)} WHERE id = {self.id}"

    @classmethod
    def get_column_type(cls, column_name: str) -> str:
        """
        Returns the data type of the column used in SQL.

        Args:
            column_name (str): The name of the column.

        Returns:
            str: The data type of the column in SQL.

        Raises:
            Exception: If the data type is not supported in SQL.

        """

        _get = getattr(cls, column_name, None)
        if isinstance(_get, Column):
            return _get.sql_type
        else:
            raise ValueError(f"Column {column_name} is not found.")

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
    
    def is_abstract(self) -> bool:
        """
        Returns whether the object is abstract or not.
        """
        return bool(self.table_name)
    
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
            self._database.insert(self.table_name, **self.get_insert_information())
            
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
        self._database.cursor.execute(self.get_update_query())
    
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

class ConcreteObject(metaclass=ABCMeta):
    
    corresponding_category: Any
    
    @classmethod
    @abstractmethod
    def create_from(self, table_object: TableObject):
        return self
    
    def get_description(self) -> str:
        file = ConcreteObjectDescription()
        return file.get(self.__class__.__name__, str(self.corresponding_category))



class HasCategoryAndAmount(metaclass=ABCMeta):
    
    def __init__(self, category:ResourceCategory, amount:int):
        self.category = category
        self.amount = amount

    def __str__(self):
        return f"{self.category.name}({self.amount})"
    
    def __int__(self):
        return int(self.amount)
    
    def _check_category(self, other:"HasCategoryAndAmount"):
        """
        같은 카테고리인지 확인
        """
        if not isinstance(other, (HasCategoryAndAmount, int)): raise TypeError(f"HasCategoryAndAmount 객체를 상속한 객체 혹은 int 객체가 아닙니다.")
        if isinstance(other, HasCategoryAndAmount) and self.category != other.category: raise ValueError("카테고리가 다릅니다.")

    def move(self, other:"HasCategoryAndAmount", *, amount:int = None):
        """
        다른 자원 객체로 자원을 이동
        """
        self._check_category(other)
        if amount is None or amount > self.amount: amount = self.amount
        
        other.amount += amount
        self.amount -= amount
    
    def __add__(self, other:"HasCategoryAndAmount | int"):
        self._check_category(other)
        if isinstance(other, int):
            self.amount += other
        else:
            self.amount += other.amount
        return self
    
    def __sub__(self, other:"HasCategoryAndAmount | int"):
        self._check_category(other)
        if isinstance(other, int):
            self.amount -= other
        else:
            self.amount -= other.amount
        return self
    
    def __lt__(self, other:"HasCategoryAndAmount | int"):
        if isinstance(other, int): return self.amount < other
        return self.category == other.category and self.amount < other.amount
    
    def __le__(self, other:"HasCategoryAndAmount | int"):
        if isinstance(other, int): return self.amount <= other
        return self.category == other.category and self.amount <= other.amount
    
    def __eq__(self, other:"HasCategoryAndAmount | int"):
        if isinstance(other, int): return self.amount == other
        return self.category == other.category and self.amount == other.amount
    
    def __ne__(self, other:"HasCategoryAndAmount | int"):
        if isinstance(other, int): return self.amount != other
        return self.category == other.category and self.amount != other.amount
    
    def __gt__(self, other:"HasCategoryAndAmount | int"):
        if isinstance(other, int): return self.amount > other
        return self.category == other.category and self.amount > other.amount
    
    def __ge__(self, other:"HasCategoryAndAmount | int"):
        if isinstance(other, int): return self.amount >= other
        return self.category == other.category and self.amount >= other.amount

class ExperienceAbst(HasCategoryAndAmount, metaclass=ABCMeta):
    
    def __init__(self, category:ExperienceCategory, amount:int):
        super().__init__(category, amount)

    @property
    def level(self):
        return int((-1 + sqrt(1 + 2/3 * self.amount)) // 2)
    
    def get_dice(self) -> D20:
        return D20(self.level)
        
# deprecated
# @dataclass
# class Storages(Facilitys, metaclass=ABCMeta):
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
#             "facility_material" : 건자재,
#             "dice_cost" : 주사위 총량
#         }
#         """
#         return {
#             "facility_material" : 10 * self.level,
#             "dict_cost" : 10 * self.level
#         }
