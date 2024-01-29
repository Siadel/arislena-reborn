"""
.db 파일과 sqlite3으로서 상호작용하는 클래스들
"""
import sqlite3

from py_base import utility
from py_system.abstract import TableObject
from py_system.tableobj import convert_to_tableobj, Faction, FactionHierarchyNode

class DatabaseManager:

    def __init__(self, db_name: str, test_mode = False):
        """
        db_name: 확장자를 포함하지 않은 파일 이름\n
        test_mode: 테스트 모드일 경우, 파일 이름에 _test를 붙여서 생성
        """
        db_name += "_test" if test_mode else ""
        self.filename = db_name + ".db"
        self.path = utility.DATA_DIR + self.filename
        self.conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self.cursor = self.conn.cursor()
    
    def __del__(self):
        self.conn.close()

    def fetch(self, table:str, *statements) -> TableObject | None:
        """
        sql 공용 검색 함수
        ---
        table을 받고, statements에 해당하는 데이터를 미리 만들어진 데이터 클래스 형태로 출력\n
        데이터가 없으면 None을 반환\n
        반환값을 받는 변수 타입은 따로 지정해야 함\n
        """
        sql = f"SELECT * FROM {table} WHERE "
        sql += " AND ".join(statements)
        self.cursor.execute(sql)

        data = self.cursor.fetchone()
        if not data:
            return None

        return convert_to_tableobj(table, data)
    
    def fetch_many(self, table:str, *statements) -> list[TableObject] | list:
        """
        sql 공용 검색 함수
        ---
        table을 받고, statements에 해당하는 데이터를 미리 만들어진 데이터 클래스 형태로 출력\n
        데이터가 없으면 빈 리스트를 반환\n
        반환값을 받는 변수 타입은 따로 지정해야 함\n
        """
        sql = f"SELECT * FROM {table} WHERE "
        for statement in statements:
            sql += f"{statement} AND "
        sql = sql[:-5]
        self.cursor.execute(sql)

        data = self.cursor.fetchall()
        if data is None:
            return []

        return [convert_to_tableobj(table, d) for d in data]

    def fetch_all(self, table:str) -> list[TableObject]:
        """
        sql 공용 전역 검색 함수
        ---
        table을 받고, statements에 해당하는 데이터를 미리 만들어진 데이터 클래스 형태로 출력\n
        데이터가 없으면 None을 반환\n
        반환값을 받는 변수 타입은 따로 지정해야 함\n
        """
        sql = f"SELECT * FROM {table}"
        self.cursor.execute(sql)

        data = self.cursor.fetchall()
        if data is None:
            return None

        return [convert_to_tableobj(table, d) for d in data]
    
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
        
        sql = f"UPDATE {table} SET "
        for key, value in kwargs.items():
            if isinstance(value, str):
                sql += f"{key} = '{value}', "
            elif value is None:
                sql += f"{key} = NULL, "
            else:
                sql += f"{key} = {value}, "
        sql = sql[:-2] + f" WHERE ID = {ID}"
        self.cursor.execute(sql)

    def update_as(self, tableobj:TableObject):
        """
        tableobj의 데이터를 받아서 업데이트
        """
        self.update_with_id(tableobj.get_table_name(), **tableobj.items)

    def delete_with_id(self, table:str, ID:int):
        """
        sql 공용 삭제 함수
        ---
        : table을 받고, ID로 데이터를 검색한 후, 해당 데이터를 삭제하기
        """
        sql = f"DELETE FROM {table} WHERE ID = {ID}"
        self.cursor.execute(sql)
    
    def insert(self, tableobj:TableObject):
        """
        sql 공용 삽입 함수
        ---
        데이터 삽입 시 ID는 자동으로 증가하므로 어떤 값으로 해도 됨
        : table을 받고, kwargs에 있는 데이터를 삽입하기
        """

        sql = f"INSERT INTO {tableobj.get_table_name()} ({tableobj.keys_string}) VALUES ({tableobj.values_string})"
        self.cursor.execute(sql)
    
    def table_column_set(self, table_name:str) -> set:
        """
        table_info로 꺼내온 정보는 id, name, type, notnull, dflt_value, pk 순서로 저장되어 있음\n
        name만 뽑아서 집합으로 저장
        """
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return set(d[1] for d in self.cursor.fetchall())

    def has_row(self, table_name:str) -> bool:
        """
        테이블에 데이터가 있는지 확인
        """
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return len(self.cursor.fetchall()) > 0

class MainDB(DatabaseManager):

    def __init__(self, test_mode = False):
        """
        - 상속
        """
        super().__init__("main", test_mode)

    def set_hierarchy(self, lower_fation:Faction, higher_faction:Faction):
        """
        계급 설정
        """
        if lower_fation.level > higher_faction.level:
            raise ValueError("하위 세력의 레벨이 상위 세력의 레벨보다 높습니다.")
        self.insert(
            FactionHierarchyNode(higher=higher_faction.ID, lower=lower_fation.ID)
        )

    def fetch_all_high_hierarchy(self, faction:Faction) -> list[Faction]:
        """
        해당 세력의 상위 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self.fetch_many("FactionHierarchyNode", f"lower = {faction.ID}")

        return [self.fetch("faction", f"ID = {node.higher}") for node in nodes]
    
    def fetch_all_low_hierarchy(self, faction:Faction) -> list[Faction]:
        """
        해당 세력의 하위 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self.fetch_many("FactionHierarchyNode", f"higher = {faction.ID}")

        return [self.fetch("faction", f"ID = {node.lower}") for node in nodes]
    
    def fetch_all_hierarchy_id(self, faction:Faction) -> list[int]:
        """
        해당 세력의 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self.fetch_many("FactionHierarchyNode", f"higher = {faction.ID} OR lower = {faction.ID}")

        return [node.ID for node in nodes]