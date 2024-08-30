from py_base.dbmanager import DatabaseManager
from py_base.ari_logger import ari_logger
from py_system import tableobj


def setup_database(database: DatabaseManager):
    
    # 테이블 생성
    tableobj.form_database_from_tableobjects(database)

    # 테이블 초기화
    for single_component_table in tableobj.SingleComponentTable.__subclasses__():
        if not database.fetch(single_component_table.table_name, id=1):
            single_component_table().set_database(database).push()
    
    if not database.fetch(tableobj.Team.table_name, id=1):
        new_team = tableobj.Team(1, "인류의 여명")\
            .set_database(database)
        new_team.push()
    
    database.connection.commit()
    
    ari_logger.info("테이블 초기화 완료")