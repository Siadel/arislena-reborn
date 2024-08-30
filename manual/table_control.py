from py_base.dbmanager import DatabaseManager

def manual_migrate_columns_with_foreign_key_handling(database: DatabaseManager, table_name: str, column_transfers: dict, columns_to_remove: list):
    """
    특정 컬럼의 데이터를 다른 컬럼으로 옮기고, 원래 컬럼을 삭제하는 수동 마이그레이션 함수.
    외래 키 제약 조건을 고려하여 컬럼 삭제를 수행합니다.
    
    :param database: DatabaseManager 인스턴스
    :param table_name: 작업할 테이블의 이름
    :param column_transfers: {기존 컬럼: 새 컬럼} 형태의 컬럼 전송 딕셔너리
    :param columns_to_remove: 삭제할 컬럼의 이름 리스트
    """
    conn = database.connection
    cursor = conn.cursor()

    try:
        # 1. 외래 키 제약 조건 비활성화
        cursor.execute("PRAGMA foreign_keys=OFF")
        print("Foreign key constraints temporarily disabled.")
        
        # 2. 테이블의 기존 구조 가져오기
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {col[1]: col[2] for col in cursor.fetchall()}  # {컬럼 이름: 데이터 타입}

        # 3. 유효성 검사
        for old_col, new_col in column_transfers.items():
            if old_col not in existing_columns:
                raise ValueError(f"기존 컬럼 {old_col}이(가) 테이블에 존재하지 않습니다.")
            if new_col in existing_columns:
                raise ValueError(f"새 컬럼 {new_col}이(가) 이미 테이블에 존재합니다.")

        if not set(columns_to_remove).issubset(existing_columns):
            raise ValueError("삭제할 컬럼 중 일부가 테이블에 존재하지 않습니다.")
        
        if set(column_transfers.keys()) & set(columns_to_remove):
            raise ValueError("같은 컬럼을 이동하고 삭제할 수 없습니다.")
        
        # 4. 새 컬럼 추가
        for old_col, new_col in column_transfers.items():
            old_col_type = existing_columns[old_col]
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_col} {old_col_type}")
            print(f"Added new column {new_col} with type {old_col_type}.")

        # 5. 데이터 이동
        for old_col, new_col in column_transfers.items():
            cursor.execute(f"UPDATE {table_name} SET {new_col} = {old_col}")
            print(f"Transferred data from {old_col} to {new_col}.")

        # 6. 임시 테이블 생성 및 데이터 복사
        remaining_columns = [col for col in existing_columns if col not in columns_to_remove] + list(column_transfers.values())
        remaining_columns_str = ", ".join(remaining_columns)
        
        temp_table_name = f"{table_name}_temp"
        cursor.execute(f"CREATE TABLE {temp_table_name} AS SELECT {remaining_columns_str} FROM {table_name}")
        print(f"Temporary table {temp_table_name} created with columns: {remaining_columns_str}")

        # 7. 기존 테이블 삭제
        cursor.execute(f"DROP TABLE {table_name}")
        print(f"Original table {table_name} dropped.")

        # 8. 임시 테이블을 원래 테이블로 이름 변경
        cursor.execute(f"ALTER TABLE {temp_table_name} RENAME TO {table_name}")
        print(f"Temporary table {temp_table_name} renamed to {table_name}")

        conn.commit()
        print(f"Data transferred and columns {', '.join(columns_to_remove)} removed successfully from table {table_name}.")

    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        # 9. 외래 키 제약 조건 재활성화
        cursor.execute("PRAGMA foreign_keys=ON")
        print("Foreign key constraints re-enabled.")
