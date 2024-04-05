"""
Sql과 연동되는 데이터 클래스들
"""
from sqlite3 import Row
from typing import ClassVar
from dataclasses import dataclass

from py_base.ari_enum import TerritorySafety, BuildingCategory, ResourceCategory, CommandCountCategory, Availability
from py_base.datatype import ExtInt
from py_base.dbmanager import MainDB
from py_system.abstract import TableObject, ResourceBase

def form_database_from_tableobjects(main_db:MainDB):
    """
    TableObject 객체를 상속하는 객체의 수만큼 테이블 생성하고, 테이블을 초기화
    만약 TableObject를 상속하는 객체의 데이터 형식이 기존의 데이터 형식과 다를 경우, 기존의 데이터를 유지하며 새로운 데이터 형식을 추가
    """
    for subclass_type in TableObject.__subclasses__():
        # TableObject를 상속하는 객체의 테이블을 생성함 (이미 존재할 경우, 무시함)
        subclass = subclass_type()
        subclass.set_database(main_db)
        main_db.cursor.execute(subclass.get_create_table_string())

        table_name = subclass.table_name
        # TableObject를 상속하는 객체의 데이터 형식과 main_db의 데이터 형식을 불러와 차이를 판별하기
        # main_db의 데이터 형식을 불러옴
        sql_table_column_set = main_db.table_column_set(table_name)

        # TableObject를 상속하는 객체의 데이터 형식을 불러옴
        tableobj_column_set = set(subclass.get_dict().keys())

        # 데이터베이스 테이블의 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교함
        # TableObject를 상속하는 객체에 없는 데이터 형식이 있을 경우, main_db에서 해당 데이터 형식을 삭제함
        for column_name in (sql_table_column_set - tableobj_column_set):
            main_db.cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
        # main_db에 없는 데이터 형식이 있을 경우, main_db에 해당 데이터 형식을 추가하고, 기본값을 넣음
        # subclass 객체는 기본값을 가지고 있다는 점을 이용함
        for column_name in (tableobj_column_set - sql_table_column_set):
            main_db.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {subclass.get_column_type(column_name)} DEFAULT {getattr(subclass, column_name)}")
        
        
        # # 데이터베이스 테이블의 데이터 형식을 다시 불러옴
        # sql_table_column_set = main_db.table_column_set(table_name)
        
        # # 이 아래의 코드가 실행되나? -> 실행되지 않음
        
        # # 새로 불러온 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교함
        # if set(sql_table_column_set) != set(tableobj_column_set):
        #     has_row = main_db.has_row(table_name)
        #     if has_row:
        #         # 테이블 데이터 임시 저장
        #         # 테이블에 데이터가 없는 경우 임시 저장할 필요 없음
        #         main_db.cursor.execute(f"CREATE TABLE {table_name}_temp AS SELECT * FROM {table_name}")
        #     # 테이블 삭제
        #     main_db.cursor.execute(f"DROP TABLE {table_name}")
        #     # 테이블 재생성
        #     main_db.cursor.execute(subclass.get_create_table_string())
        #     if has_row:
        #         # 임시 저장 테이블의 column마다 작업하여 테이블 데이터 복원
        #         # 임시 저장 테이블의 데이터를 {key:value} 형식으로 변환함
        #         main_db.cursor.execute(f"SELECT * FROM {table_name}_temp")
        #         backup_data = [subclass_type.from_data(row) for row in main_db.cursor.fetchall()]
                
        #         # 임시 저장 테이블의 데이터를 새로운 테이블에 삽입함
        #         for data in backup_data:
        #             data.push()
        #         # 임시 저장 테이블 삭제
        #         main_db.cursor.execute(f"DROP TABLE {table_name}_temp")
    
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
액티브 데이터
"""
@dataclass
class User(TableObject):

    id: int = 0
    discord_id:int = 0
    discord_name:str = ""
    register_date:str = ""
    
    def get_display_string(self) -> str:
        return str(self.discord_name)

@dataclass
class Resource(TableObject, ResourceBase):

    id: int = 0
    faction_id: int = 0
    category: ResourceCategory = ResourceCategory.UNSET
    amount: ExtInt = ExtInt(0, min_value=0)
    
    def get_display_string(self) -> str:
        return self.category.local_name

@dataclass
class Crew(TableObject):

    id: int = 0
    faction_id:int = 0
    name:str = ""
    labor:int = 1
    food_consumption:int = 1
    water_consumption:int = 1
    availability: Availability = Availability.UNAVAILABLE
    
    def get_display_string(self) -> str:
        return self.name
    
    def is_available(self) -> bool:
        return self.availability.is_available()
    
@dataclass
class Livestock(TableObject):

    id: int = 0
    faction_id:int = 0
    labor:int = 1
    feed_consumption:int = 1
    availability: Availability = Availability.UNAVAILABLE
    
    def get_display_string(self) -> str:
        return f"가축 {self.id}"

@dataclass
class FactionHierarchyNode(TableObject):

    id: int = 0
    higher:int = 0
    lower:int = 0
    
    def get_display_string(self) -> str:
        return f"{self.higher} -> {self.lower}"
    
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
class Territory(TableObject):

    id: int = 0
    faction_id: int = 0
    name: str = ""
    space_limit: int = 1
    safety: TerritorySafety = TerritorySafety.UNKNOWN

    def get_display_string(self) -> str:
        return self.name

    def explicit_post_init(self):
        """
        안전도를 랜덤으로 설정함
        """
        if self.safety == TerritorySafety.UNKNOWN:
            self.safety = TerritorySafety.get_randomly()
    
    @property
    def remaining_space(self) -> int:
        """
        남은 공간
        """
        return self.space_limit - len(self._database.fetch_many("building", territory_id=self.id))


@dataclass
class Deployment(TableObject):
    
    id: int = 0
    crew_id: int = None
    territory_id: int = None
    building_id: int = None
    
    def get_display_string(self) -> str:
        return f"배치 현황 {self.id}"

@dataclass
class Building(TableObject):

    id: int = 0
    faction_id: int = 0
    territory_id: int = 0
    category: BuildingCategory = BuildingCategory.UNSET
    name: str = ""
    remaining_dice_cost: int = 0
    level: int = 0

    def get_display_string(self) -> str:
        return self.name
    
    @property
    def deploy_limit(self) -> int:
        return self.level + 2
    
    def is_deployable(self, deployed_crew_ids: list[int] = None) -> bool:
        if not self.is_built(): return True
        
        if deployed_crew_ids is None:
            deployed_crew_ids = self.get_deployed_crew_ids()
        
        if len(deployed_crew_ids) >= self.deploy_limit: return False
        return True
    
    def deploy(self, crew: Crew):
        """
        건물에 인원 배치
        
        건물 완공 여부, 건물 배치 인원 제한 여부, 이미 배치된 인원 여부를 확인함
        """
        self._check_database()
        
        deployment = Deployment(crew_id=crew.id, territory_id=self.territory_id, building_id=self.id)
        deployment.set_database(self._database)
        deployment.push()
        
    def apply_production(self, dice:int):
        if self.is_built():
            raise ValueError("건물이 완공되었습니다.")
        self.remaining_dice_cost = max(0, self.remaining_dice_cost - dice)
    
    def is_built(self) -> bool:
        """
        건물이 완공되었는지 확인
        """
        return self.remaining_dice_cost == 0
    
    def get_deployed_crew_ids(self) -> list[int]:
        """
        건물에 배치된 인원의 ID를 가져옴
        """
        self._check_database()
        ids:list[Row] = self._database.cursor.execute("SELECT crew_id FROM deployment WHERE building_id = ?", (self.id,)).fetchall()
        return [id[0] for id in ids]
    
    def get_deployed_crews(self) -> list[Crew]:
        """
        건물에 배치된 인원을 가져옴
        """
        self._check_database()
        deployments = list[Deployment] = [Deployment.from_data(data) for data in self._database.fetch_many("deployment", building_id=self.id)]
        return [Crew.from_data(self._database.fetch("crew", id=deployment.crew_id)) for deployment in deployments]

@dataclass
class CommandCounter(TableObject):
    
    id: int = 0
    faction_id: int = 0
    category: CommandCountCategory = CommandCountCategory.UNSET
    amount: int = 0
    
    def get_display_string(self) -> str:
        return self.category.local_name
    
    def reset(self):
        """
        값 초기화
        """
        self.amount = 0
                
    def increase(self):
        """
        amount를 1 증가시킴
        """
        self.amount += 1

@dataclass
class Faction(TableObject):
    
    id: int = 0
    user_id: int = 0
    name: str = ""
    level: int = 0

    def get_display_string(self) -> str:
        return self.name
    
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
        if not r: return Resource(faction_id=self.id, category=category)
        return Resource.from_data(r)
    
    def get_crew(self, name:str) -> Crew:
        """
        해당 세력의 인구를 가져옴
        """
        cr = self._database.fetch("crew", faction_id=self.id, name=name)

        if not cr: return Crew(faction_id=self.id, name=name)
        return Crew.from_data(cr)
    
    def get_command_counter(self, category:CommandCountCategory) -> CommandCounter:
        """
        해당 세력의 명령 카운터를 가져옴
        """
        cc = self._database.fetch("CommandCounter", faction_id=self.id, category=category.value)
        if not cc: return CommandCounter(faction_id=self.id, category=category)
        return CommandCounter.from_data(cc)
