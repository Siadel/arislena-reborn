"""
.db 파일과 sqlite3으로서 상호작용하는 클래스들
"""
import sqlite3
from pathlib import Path
from typing import Iterable, Any
from datetime import datetime
import shutil

from py_base.ari_logger import ari_logger
from py_base.utility import DATA_DIR, sql_value, FULL_DATE_FORMAT_NO_SPACE

ON_DELETE_CASCADE = "ON DELETE CASCADE"
ON_DELETE_SET_NULL = "ON DELETE SET NULL"
ON_UPDATE_CASCADE = "ON UPDATE CASCADE"


def log_query(query:str):
    ari_logger.debug(f"[SQL]\t{query}")

class DatabaseManager:

    def __init__(self, stem: str):
        """
        stem: 확장자를 포함하지 않은 파일 이름
        """
        self.stem = stem
        self.file_path = Path(DATA_DIR, stem + ".db")
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
        
    def fetch_core(self, table: str, *raw_statements, **statements) -> sqlite3.Cursor:
        if not (raw_statements or statements): raise ValueError("At least one statement is required.")
        
        s = [f"{key} = {sql_value(value)}" for key, value in statements.items()]
        s += list(raw_statements)
        
        sql = f"SELECT * FROM {table} WHERE {' AND '.join(s)}"
        self.cursor.execute(sql)

    def fetch(self, table:str, *raw_statements, **statements) -> sqlite3.Row | None:
        """
        조건에 맞는 데이터 하나를 가져옴
        
        (조건에 맞는 데이터가 많으면, 그 중 id값이 가장 작은 데이터를 가져옴)
        """
        return self.fetch_core(table, *raw_statements, **statements).fetchone()

    def is_exist(self, table:str, *raw_statements, **statements) -> bool:
        """
        조건에 맞는 데이터가 있는지 확인
        """
        return self.fetch(table, *raw_statements, **statements) is not None

    
    def fetch_many(self, table:str, *raw_statements, **statements) -> list[sqlite3.Row]:
        """
        조건에 맞는 여러 행을 가져옴
        """

        return self.fetch_core(table, *raw_statements, **statements).fetchall()

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
    
    def fetch_column(self, table:str, column:str, *statements) -> list[sqlite3.Row]:
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
        keys_iter = [f"{key} = ?" for key in kwargs.keys()]
        values_iter = list(kwargs.values()) + [ID]
        sql = f"UPDATE {table} SET {', '.join(keys_iter)} WHERE ID = ?"
        self.cursor.execute(sql, values_iter)

    def delete_with_id(self, table:str, ID:int):
        """
        sql 공용 삭제 함수
        ---
        : table을 받고, ID로 데이터를 검색한 후, 해당 데이터를 삭제하기
        """
        sql = f"DELETE FROM {table} WHERE ID = ?"
        self.cursor.execute(sql, (ID,))
    
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
        sql = f"INSERT INTO {table_name} ({', '.join(keys_iter)}) VALUES ({', '.join('?' for _ in values_iter)})"
        self.cursor.execute(sql, values_iter)
    
    def get_table_column_set(self, table_name:str) -> set:
        """
        table_info로 꺼내온 정보는 id, name, type, notnull, dflt_value, pk 순서로 저장되어 있음\n
        name만 뽑아서 집합으로 저장
        """
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return set(table_info["name"] for table_info in self.cursor.fetchall())
    
    def get_all_table_names(self) -> set[str]:
        """
        데이터베이스에 있는 모든 테이블 이름을 반환함
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {table_info["name"] for table_info in self.cursor.fetchall() if table_info["name"] != "sqlite_sequence"}

    def has_row(self, table_name:str) -> bool:
        """
        테이블에 데이터가 있는지 확인
        """
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return len(self.cursor.fetchall()) > 0
    
    def backup(self, directory: Path) -> str:
        """
        지정된 디렉토리에 백업을 생성하고, 백업 파일의 경로를 반환함.
        """
        backup_path = Path(directory, f"{self.stem}_{datetime.now().strftime(FULL_DATE_FORMAT_NO_SPACE)}_backup.db")
        shutil.copy2(self.file_path, backup_path)
        return backup_path




