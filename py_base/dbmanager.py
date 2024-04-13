"""
.db 파일과 sqlite3으로서 상호작용하는 클래스들
"""
import sqlite3
from pathlib import Path
from typing import Iterable, Any

from py_base.ari_logger import ari_logger
from py_base.utility import DATA_DIR, sql_value

def log_query(query:str):
    ari_logger.debug(f"[SQL]\t{query}")

class DatabaseManager:

    def __init__(self, db_stem: str):
        """
        db_name: 확장자를 포함하지 않은 파일 이름
        """
        self.file_path = Path(DATA_DIR, db_stem + ".db")
        self.connection = sqlite3.connect(
            self.file_path, 
            check_same_thread=False 
            # isolation_level=None
        )
        self.connection.set_trace_callback(log_query)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
    
    def __del__(self):
        self.connection.close()

    def fetch(self, table:str, *raw_statements, **statements) -> sqlite3.Row | None:
        """
        Fetches a single row from the specified table in the database based on the provided statements.

        Args:
            `table (str)`: The name of the table to fetch the row from.
            `*raw_statements`: Raw SQL statements to include in the WHERE clause.
            `**statements`: Keyword arguments representing the column-value pairs to filter the row.

        Returns:
            `sqlite3.Row | None`: The fetched row as a `sqlite3.Row` object, or `None` if no matching row is found.
        
        Raises:
            `ValueError`: If no statement is provided.

        Example:
            ```python
            row = db.fetch("users", username="john_doe")
            print(row["id"], row["username"], row["email"])
            ```
        
        Notes:
            - If multiple rows match the provided statements, only the first row is returned.
            - Based on the provided statements, the WHERE clause is constructed using the `AND` operator. To use other operators, use raw SQL statements. (This explanation is also available in the `fetch_many` method.)
        """
        if not (raw_statements or statements): raise ValueError("At least one statement is required.")

        s = [f"{key} = {sql_value(value)}" for key, value in statements.items()]
        s += list(raw_statements)
        
        sql = f"SELECT * FROM {table} WHERE {' AND '.join(s)}"
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def is_exist(self, table:str, *raw_statements, **statements) -> bool:
        """
        Checks if a row exists in the specified table in the database based on the provided statements.

        Args:
            `table (str)`: The name of the table to check the row from.
            `*raw_statements`: Raw SQL statements to include in the WHERE clause.
            `**statements`: Keyword arguments representing the column-value pairs to filter the row.

        Returns:
            `bool`: `True` if a matching row is found, `False` otherwise.
        
        Raises:
            `ValueError`: If no statement is provided.

        Example:
            ```python
            print(db.is_exist("users", username="john_doe"))
            ```
        """
        if not (raw_statements or statements): raise ValueError("At least one statement is required.")

        s = [f"{key} = {sql_value(value)}" for key, value in statements.items()]
        s += list(raw_statements)
        
        sql = f"SELECT id FROM {table} WHERE {' AND '.join(s)}"
        self.cursor.execute(sql)
        return self.cursor.fetchone() is not None

    
    def fetch_many(self, table:str, *raw_statements, **statements) -> list[sqlite3.Row]:
        """
        Fetches multiple rows from the specified table based on the provided statements.

        Args:
            `table (str)`: The name of the table to fetch data from.
            `*raw_statements`: Raw SQL statements to be included in the WHERE clause.
            `**statements`: Key-value pairs representing column names and their corresponding values for filtering.

        Returns:
            `list[sqlite3.Row]`: A list of rows fetched from the table. If no matching rows are found, an empty list is returned.

        Raises:
            `ValueError`: If no statements are provided.
        """
        
        if not (raw_statements or statements): raise ValueError("At least one statement is required.")

        s = [f"{key} = {sql_value(value)}" for key, value in statements.items()]
        s += list(raw_statements)

        sql = f"SELECT * FROM {table} WHERE {' AND '.join(s)}"
        self.cursor.execute(sql)

        return self.cursor.fetchall()

    def fetch_all(self, table:str) -> list[sqlite3.Row]:
        """
        Fetches all rows from the specified table in the database.

        Args:
            table (str): The name of the table to fetch data from.

        Returns:
            list[sqlite3.Row]: A list of rows fetched from the table.
        """
        sql = f"SELECT * FROM {table}"
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    def fetch_column(self, table:str, column:str, *statements) -> list:
        """
        sql 공용 검색 함수
        ---
        table을 받고, statements에 해당하는 데이터를 리스트 형태로 출력\n
        데이터가 없으면 None을 반환\n
        반환값을 받는 변수 타입은 따로 지정해야 함\n
        statements가 없으면 추가 조건 없이 모든 행의 데이터를 가져옴
        """
        if len(statements) == 0:
            sql = f"SELECT {column} FROM {table}"
        else:
            sql = f"SELECT {column} FROM {table} WHERE "
            sql += " AND ".join(statements)
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        if data is None:
            return None

        return [d[0] for d in data]

    def update_with_id(self, table:str, ID:int, **kwargs):
        """
        sql 공용 업데이트 함수
        ---
        : table을 받고, ID로 데이터를 검색한 후, kwargs에 있는 데이터를 수정하기
        """
        components = [f"{key} = {sql_value(value)}" for key, value in kwargs.items()]
        sql = f"UPDATE {table} SET {', '.join(components)} WHERE ID = {ID}"
        self.cursor.execute(sql)

    def delete_with_id(self, table:str, ID:int):
        """
        sql 공용 삭제 함수
        ---
        : table을 받고, ID로 데이터를 검색한 후, 해당 데이터를 삭제하기
        """
        sql = f"DELETE FROM {table} WHERE ID = {ID}"
        self.cursor.execute(sql)
    
    def insert(self, table_name:str, keys_iter:Iterable[str], values_iter:Iterable[Any]):
        """
        Insert a new row into the specified table.

        Args:
            table_name (str): The name of the table.
            keys_iter (Iterable): An iterable containing the column names.
            values_iter (Iterable): An iterable containing the values to be inserted.

        Returns:
            None
        """
        sql = f"INSERT INTO {table_name} ({', '.join(keys_iter)}) VALUES ({', '.join(sql_value(v) for v in values_iter)})"
        self.cursor.execute(sql)
    
    def table_column_set(self, table_name:str) -> set:
        """
        table_info로 꺼내온 정보는 id, name, type, notnull, dflt_value, pk 순서로 저장되어 있음\n
        name만 뽑아서 집합으로 저장
        """
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return set(table_info["name"] for table_info in self.cursor.fetchall())

    def has_row(self, table_name:str) -> bool:
        """
        테이블에 데이터가 있는지 확인
        """
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return len(self.cursor.fetchall()) > 0

class MainDB(DatabaseManager):

    def __init__(self):
        """
        Initializes the DBManager object.

        Parameters:
        - test_mode (bool): Indicates whether the DBManager is in test mode or not. Default is False.
        
        Raises:
        - Exception: If the DBManager is already instantiated.

        """
        
        super().__init__("main")

