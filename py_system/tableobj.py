"""
Sql과 연동되는 데이터 클래스들
"""

from typing import ClassVar
from dataclasses import dataclass

from py_base.ari_enum import YesNo, TerritorySafety, BuildingCategory, ResourceCategory
from py_base.datatype import ExtInt
from py_base.dbmanager import MainDB
from py_base.abstract import TableObject, ResourceBase

def form_database_from_tableobjects(main_db:MainDB):
    """
    TableObject 객체를 상속하는 객체의 수만큼 테이블 생성하고, 테이블을 초기화
    만약 TableObject를 상속하는 객체의 데이터 형식이 기존의 데이터 형식과 다를 경우, 기존의 데이터를 유지하며 새로운 데이터 형식을 추가
    """
    for subclass in TableObject.__subclasses__():
        # TableObject를 상속하는 객체의 테이블을 생성함 (이미 존재할 경우, 무시함)
        subclass = subclass()
        main_db.cursor.execute(subclass.get_create_table_string())

        table_name = subclass.table_name
        # TableObject를 상속하는 객체의 데이터 형식과 main_db의 데이터 형식을 불러와 차이를 판별하기
        # main_db의 데이터 형식을 불러옴
        sql_table_column_set = main_db.table_column_set(table_name)

        # TableObject를 상속하는 객체의 데이터 형식을 불러옴
        tableobj_column_set = set(subclass.__dict__.keys())

        # 데이터베이스 테이블의 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교함
        # TableObject를 상속하는 객체에 없는 데이터 형식이 있을 경우, main_db에서 해당 데이터 형식을 삭제함
        for column_name in (sql_table_column_set - tableobj_column_set):
            main_db.cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
        # main_db에 없는 데이터 형식이 있을 경우, main_db에 해당 데이터 형식을 추가함
        for column_name in (tableobj_column_set - sql_table_column_set):
            main_db.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {subclass.get_column_type(column_name)}")
        
        # 데이터베이스 테이블의 데이터 형식을 다시 불러옴
        sql_table_column_set = main_db.table_column_set(table_name)
        
        # 새로 불러온 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교함
        if set(sql_table_column_set) != set(tableobj_column_set):
            has_row = main_db.has_row(table_name)
            if has_row:
                # 테이블 데이터 임시 저장
                # 테이블에 데이터가 없는 경우 임시 저장할 필요 없음
                main_db.cursor.execute(f"CREATE TABLE {table_name}_temp AS SELECT * FROM {table_name}")
            # 테이블 삭제
            main_db.cursor.execute(f"DROP TABLE {table_name}")
            # 테이블 재생성
            main_db.cursor.execute(subclass.get_create_table_string())
            if has_row:
                # 임시 저장 테이블의 column마다 작업하여 테이블 데이터 복원
                # 임시 저장 테이블의 데이터를 {key:value} 형식으로 변환함
                main_db.cursor.execute(f"SELECT * FROM {table_name}_temp")
                backup_data = [dict(zip([column[0] for column in main_db.cursor.description], data)) for data in main_db.cursor.fetchall()]
                # 임시 저장 테이블의 데이터를 새로운 테이블에 삽입함
                for data in backup_data:
                    # TODO 이거 다시 짜야 해!!
                    main_db.insert(subclass.table_name, data.keys(), data.values())
                # 임시 저장 테이블 삭제
                main_db.cursor.execute(f"DROP TABLE {table_name}_temp")
    
    # 데이터베이스의 테이블 목록 불러오기
    main_db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables: set[str] = {table[0] for table in main_db.cursor.fetchall()}
    tables.remove("sqlite_sequence")
    # TableObject를 상속하는 객체의 테이블 목록 불러오기
    tableobj_tables: set[str] = {subclass().table_name for subclass in TableObject.__subclasses__()}
    
    # 데이터베이스에 존재하지 않는 테이블을 삭제함
    for table in (tables - tableobj_tables):
        main_db.cursor.execute(f"DROP TABLE {table}")
    
    main_db.connection.commit()
    
    print("Database initialized")

"""
!! ---------------------- 주의 ---------------------- !!

abstract variables: __slots__, display_column
abstract properties: kr_list
"""

"""
액티브 데이터
"""
@dataclass
class User(TableObject):

    id: int = 0
    discord_id:int = 0
    discord_name:str = ""
    register_date:str = ""

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = "discord_name"
    en_kr_map: ClassVar[dict[str, str]] = {
        "id": "아이디",
        "discord_id": "디스코드 아이디",
        "discord_name": "디스코드 이름",
        "register_date": "가입일"
    }

@dataclass
class Resource(TableObject, ResourceBase):

    id: int = 0
    faction_id: int = 0
    category: ResourceCategory = ResourceCategory.UNSET
    amount: ExtInt = ExtInt(0, min_value=0)

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = "id"
    en_kr_map: ClassVar[dict[str, str]] = {
        "id": "아이디",
        "faction_id": "세력 아이디",
        "category": "카테고리",
        "amount": "수량"
    }
    category_en_kr_map: ClassVar[dict[str, str]] = {
        "WATER": "물",
        "FOOD": "식량",
        "FEDD": "사료",
        "WOOD": "목재",
        "SOIL": "흙",
        "STONE": "석재",
        "BUILDING_MATERIAL": "건축자재"
    }

@dataclass
class Population(TableObject):

    id: int = 0
    faction_id:int = 0
    name:str = ""
    labor:int = 1
    food_consumption:int = 1
    water_consumption:int = 1
    is_laboring:YesNo = YesNo.NO

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = "name"
    en_kr_map: ClassVar[dict[str, str]] = {
        "id": "아이디",
        "faction_id": "세력 아이디",
        "name": "이름",
        "labor": "노동력",
        "food_consumption": "식량 소비",
        "water_consumption": "물 소비",
        "is_laboring": "노동 중"
    }

@dataclass
class FactionHierarchyNode(TableObject):

    id: int = 0
    higher:int = 0
    lower:int = 0

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = "higher"
    en_kr_map: ClassVar[dict[str, str]] = {
        "id": "아이디",
        "higher": "상위 세력",
        "lower": "하위 세력"
    }
    
    def push(self, lower_fation:"Faction", higher_faction:"Faction"):
        """
        계급 설정
        """
        if lower_fation.level > higher_faction.level:
            raise ValueError("하위 세력의 레벨이 상위 세력의 레벨보다 높습니다.")
        self.higher = higher_faction.id
        self.lower = lower_fation.id
        super().push()


@dataclass
class Livestock(TableObject):

    id: int = 0
    faction_id:int = 0
    labor:int = 1
    feed_consumption:int = 1
    is_laboring:YesNo = YesNo.NO

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = "ID"
    en_kr_map: ClassVar[dict[str, str]] = {
        "id": "아이디",
        "faction_id": "세력 아이디",
        "labor": "노동력",
        "feed_consumption": "사료 소비",
        "is_laboring": "노동 중"
    }


@dataclass
class Territory(TableObject):

    id: int = 0
    faction_id: int = 0
    name: str = ""
    space_limit: int = 1
    safety: TerritorySafety = TerritorySafety.UNKNOWN

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = "name"
    en_kr_map: ClassVar[dict[str, str]] = {
        "id": "아이디",
        "faction_id": "세력 아이디",
        "name": "이름",
        "space_limit": "공간 제한",
        "safety": "안정도"
    }

    def explicit_post_init(self):
        """
        안전도를 랜덤으로 설정함
        """
        if self.safety == TerritorySafety.UNKNOWN:
            self.safety = TerritorySafety.get_randomly()

@dataclass
class Building(TableObject):

    id: int = 0
    territory_id:int = 0
    discriminator:BuildingCategory = BuildingCategory.UNSET
    name:str = ""

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = "name"
    en_kr_map: ClassVar[dict[str, str]] = {
        "id": "아이디",
        "territory_id": "영토 아이디",
        "discriminator": "구분",
        "name": "이름"
    }
    
    def set_randomly_discriminator(self):
        self.discriminator = BuildingCategory.get_ramdomly_base_building()

@dataclass
class Faction(TableObject):
    
    id: int = 0
    user_id:int = 0
    name:str = ""
    level:int = 0

    _database: ClassVar[MainDB] = None
    display_column: ClassVar[str] = "name"
    en_kr_map: ClassVar[dict[str, str]] = {
        "id": "아이디",
        "user_id": "유저 아이디",
        "name": "세력명",
        "level": "레벨"
    }
    
    def fetch_all_high_hierarchy(self) -> list[FactionHierarchyNode]:
        """
        해당 세력의 상위 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self._database.fetch_many("FactionHierarchyNode", f"lower = {self.id}")

        return nodes
    
    def fetch_all_low_hierarchy(self) -> list[FactionHierarchyNode]:
        """
        해당 세력의 하위 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self._database.fetch_many("FactionHierarchyNode", f"higher = {self.id}")

        return nodes
    
    def fetch_all_hierarchy_id(self) -> list[int]:
        """
        해당 세력의 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self._database.fetch_many("FactionHierarchyNode", f"higher = {self.id} OR lower = {self.id}")

        return nodes
    
    def get_resource(self, category:ResourceCategory) -> Resource:
        """
        해당 세력의 자원을 가져옴
        """
        r = self._database.fetch("resource", faction_id=self.id, category=category.value)
        if not r: return Resource(faction_id=self.id, category=ResourceCategory(category))
        return Resource.from_data(r)
    
    def get_population(self, name:str) -> Population:
        """
        해당 세력의 인구를 가져옴
        """
        p = self._database.fetch("population", faction_id=self.id, name=name)

        if not p: return Population(faction_id=self.id, name=name)
        return Population.from_data(p)