"""
Sql과 연동되는 데이터 클래스들
"""
import datetime
from sqlite3 import Row
from math import sqrt
from abc import ABCMeta
from typing import Generator

from py_base.utility import sql_value, DATE_EXPR
from py_base.ari_logger import ari_logger
from py_base.ari_enum import TerritorySafety, BuildingCategory, ResourceCategory, CommandCountCategory, Availability, ScheduleState, WorkerDetail, WorkCategory, WorkerCategory
from py_base.datatype import ExtInt
from py_base.dbmanager import DatabaseManager
from py_base.arislena_dice import Nonahedron
from py_base.yamlobj import Detail
from py_system.abstract import TableObject, ResourceAbst, Workable

def form_database_from_tableobjects(main_db:DatabaseManager):
    """
    TableObject 객체를 상속하는 객체의 수만큼 테이블 생성하고, 테이블을 초기화
    만약 TableObject를 상속하는 객체의 데이터 형식이 기존의 데이터 형식과 다를 경우, 기존의 데이터를 유지하며 새로운 데이터 형식을 추가
    """
    
    for subclass_type in TableObject.__subclasses__():
        # TableObject를 상속하는 추상 클래스는 무시함
        if subclass_type.abstract: continue
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
            main_db.cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {subclass.get_column_type(column_name)} DEFAULT {sql_value(getattr(subclass, column_name))}"
            )
    
    # 데이터베이스의 테이블 목록 불러오기
    main_db.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables: set[str] = {table[0] for table in main_db.cursor.fetchall()}
    tables.remove("sqlite_sequence")
    # TableObject를 상속하는 객체의 테이블 목록 불러오기
    tableobj_tables: set[str] = {subclass().table_name for subclass in TableObject.__subclasses__()}
    
    # 데이터베이스에 존재하지 않는 테이블을 삭제함
    for table in (tables - tableobj_tables):
        main_db.cursor.execute(f"DROP TABLE {table}")
        
    # Schedule 테이블에 요소가 없을 경우, 새 요소를 추가함
    for single_component_table in SingleComponentTable.__subclasses__():
        if not main_db.fetch(single_component_table.get_table_name(), id=1):
            single_component_table().set_database(main_db).push()
    
    main_db.connection.commit()
    
    ari_logger.info("Database initialized")

class Inventory(metaclass=ABCMeta):
    """
    인벤토리처럼 활용되는 객체
    """
    # TODO

class SingleComponentTable(TableObject, metaclass=ABCMeta):
    abstract = True
    
    def __init__(self, id: int = 1):
        super().__init__(id)
    
    @classmethod
    def from_database(cls, database: DatabaseManager):
        return super().from_database(database, id=1)
    
    @classmethod
    def get_table_name(cls) -> str:
        return "__" + super().get_table_name() + "__"
    
    def get_display_string(self) -> str:
        return ""

"""
액티브 데이터
"""

class Chalkboard(SingleComponentTable, TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 1,
        test_mode: bool = True,
        admin_mode: bool = False,
        start_date: str = (datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPR),
        end_date: str = "",
        now_turn: int = 0,
        turn_limit: int = 9999,
        state: ScheduleState = ScheduleState.WAITING
    ):
        super().__init__(id)
        self.test_mode = test_mode
        self.admin_mode = admin_mode
        self.start_date = start_date
        self.end_date = end_date
        self.now_turn = now_turn
        self.turn_limit = turn_limit
        self.state = state

class JobSetting(SingleComponentTable, TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 1,
        trigger: str = "cron",
        day_of_week: str = "mon, tue, wed, thu, fri, sat, sun",
        hour: str = "21",
        minute: str = "00"
    ):
        super().__init__(id)
        self.trigger = trigger
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute

class GuildSetting(SingleComponentTable, TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 1,
        announce_channel_id: int = 0,
        user_role_id: int = 0,
        admin_role_id: int = 0
    ):
        super().__init__(id)
        self.announce_channel_id = announce_channel_id
        self.user_role_id = user_role_id
        self.admin_role_id = admin_role_id

class User(TableObject):
    abstract = False
    def __init__(
        self, 
        id: int = 0,
        discord_id: int = 0, 
        discord_name: str = "", 
        register_date: str = ""
    ):
        super().__init__(id)
        self.discord_id = discord_id
        self.discord_name = discord_name
        self.register_date = register_date
    
    def get_display_string(self) -> str:
        return str(self.discord_name)


class Resource(TableObject, ResourceAbst):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        category: ResourceCategory = ResourceCategory.UNSET,
        amount: ExtInt = ExtInt(0, min_value=0)
    ):
        TableObject.__init__(self, id)
        ResourceAbst.__init__(self, category, amount)
        self.faction_id = faction_id
    
    def get_display_string(self) -> str:
        return self.category.local_name

class WorkerExperience(TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        worker_id: int = 0,
        category: WorkCategory = WorkCategory.UNSET,
        experience: int = 0
    ):
        TableObject.__init__(self, id)
        self.worker_id = worker_id
        self.category = category
        self.experience = experience

    def __int__(self):
        return self.experience
    
    @property
    def level(self) -> int:
        """
        experience와 dice mod의 상관관계
        experience가 12*(목표 mod 수치)만큼 오를 때마다 dice mod가 1씩 증가함
        ```
        0 -> +0
        12 -> +1
        36 (== 12 + 24) -> +2
        72 (== 12 + 24 + 36) -> +3
        120 (== 12 + 24 + 36 + 48) -> +4
        ...
        req. experience = 6 * mod * (mod + 1)
        mod = (-1 + sqrt(1 + 2/3 * experience)) // 2
        ```
        """
        return (-1 + sqrt(1 + 2/3 * self.experience)) // 2
        
    @classmethod
    def new(cls, worker_id: int, category: WorkCategory):
        return cls(worker_id=worker_id, experience_category=category)
    
    def get_labor_dice(self) -> Nonahedron:
        return Nonahedron(self.level)
    
    def get_display_string(self) -> str:
        return self.category.local_name
    
    def to_discord_text(self) -> str:
        return f"- {self.category.express()} : {self.experience}"

class WorkerDescription(TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        worker_id: int = 0,
        worker_labor_detail: str = "",
        ps_0: str = "",
        ps_1: str = "",
        ps_2: str = ""
    ):
        TableObject.__init__(self, id)
        self.worker_id = worker_id
        self.worker_labor_detail = worker_labor_detail
        self.ps_0 = ps_0
        self.ps_1 = ps_1
        self.ps_2 = ps_2
    
    @classmethod
    def new(cls, worker_id: int):
        desc = Detail().get_random_worker_descriptions(3)
        return cls(worker_id=worker_id, ps_0=desc[0], ps_1=desc[1], ps_2=desc[2])
    
    def set_worker_labor_detail(self, labor_dice_judge_value: int):
        detail = WorkerDetail(labor_dice_judge_value)
        self.labor_detail = detail.get_random_detail()
        return self
    
    def get_display_string(self) -> str:
        return self.worker_id
    
    def get_list(self) -> list[str]:
        return [self.ps_0, self.ps_1, self.ps_2]

class Worker(TableObject):
    abstract = False
    correspond_category: WorkerCategory = None
    
    def _check_category(self):
        if self.__class__.correspond_category is not None and self.category != self.__class__.correspond_category:
            raise ValueError("카테고리가 일치하지 않습니다.")
    
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        category: WorkerCategory = WorkerCategory.UNSET,
        name: str = "",
        labor: int = 0,
        availability: Availability = Availability.UNAVAILABLE
    ):
        TableObject.__init__(self, id)
        self.faction_id = faction_id
        self.category = category
        self.name = name
        self.labor = labor
        self.availability = availability
        
        self._check_category()
        
    @classmethod
    def get_table_name(cls) -> str:
        return Worker.__name__
    
    def get_display_string(self) -> str:
        return self.name

class FactionHierarchyNode(TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        higher: int = 0,
        lower: int = 0
    ):
        super().__init__(id)
        self.higher = higher
        self.lower = lower
    
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




class Territory(TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        name: str = "",
        space_limit: int = 1,
        safety: TerritorySafety = TerritorySafety.UNKNOWN
    ):
        super().__init__(id)
        self.faction_id = faction_id
        self.name = name
        self.space_limit = space_limit
        self.safety = safety

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


class Deployment(TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        worker_id: int = -1,
        territory_id: int = -1,
        building_id: int = -1
    ):
        super().__init__(id)
        self.worker_id = worker_id
        self.territory_id = territory_id
        self.building_id = building_id
    
    def get_display_string(self) -> str:
        return f"배치 현황 {self.id}"
    
    def get_worker(self) -> Worker:
        """
        배치된 인원을 가져옴
        """
        return Worker.from_data(self._database.fetch(Worker.get_table_name(), id=self.worker_id))

    def get_building(self) -> "Building":
        """
        배치된 건물을 가져옴
        """
        return Building.from_data(self._database.fetch(Building.get_table_name(), id=self.building_id))
    
    @classmethod
    def get_unique_building_ids(cls, database: DatabaseManager) -> Generator[int, None, None]:
        for row in database.cursor.execute(f"SELECT DISTINCT building_id FROM {cls.get_table_name()}").fetchall():
            yield row[0]


class Building(TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        territory_id: int = 0,
        category: BuildingCategory = BuildingCategory.UNSET,
        name: str = "",
        remaining_dice_cost: int = 0,
        level: int = 0
    ):
        super().__init__(id)
        self.faction_id = faction_id
        self.territory_id = territory_id
        self.category = category
        self.name = name
        self.remaining_dice_cost = remaining_dice_cost
        self.level = level
    
    @property
    def deploy_limit(self) -> int:
        return self.level + 2

    def get_display_string(self) -> str:
        return self.name
    
    def is_deployable(self, deployed_worker_ids: list[int] = None) -> bool:
        if not self.is_built(): return True
        
        if deployed_worker_ids is None:
            deployed_worker_ids = self.get_deployed_worker_ids()
        
        if len(deployed_worker_ids) >= self.deploy_limit: return False
        return True
    
    def deploy(self, worker: Worker):
        """
        건물에 인원 배치
        
        건물 완공 여부, 건물 배치 인원 제한 여부, 이미 배치된 인원 여부를 확인함
        
        이전 배치 정보가 존재하는 경우 삭제
        """
        self._check_database()
        self._database.connection.execute(
            f"DELETE FROM Deployment WHERE worker_id = {worker.id}"
        )
        deployment = Deployment(worker_id=worker.id, territory_id=self.territory_id, building_id=self.id)
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
    
    def get_deployed_worker_ids(self) -> list[int]:
        """
        건물에 배치된 인원의 ID를 가져옴
        
        ! database가 필요함
        """
        self._check_database()
        ids:list[Row] = self._database.cursor.execute("SELECT worker_id FROM deployment WHERE building_id = ?", (self.id,)).fetchall()
        return [id[0] for id in ids]
    
    def get_deployed_workers(self, deployment_list: list[Deployment]) -> list[Worker]:
        """
        건물에 배치된 인원을 가져옴
        
        ! database가 필요함
        """
        self._check_database()
        return [deployment.get_worker() for deployment in deployment_list if deployment.worker_id is not None]


class CommandCounter(TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        category: CommandCountCategory = CommandCountCategory.UNSET,
        amount: int = 0
    ):
        super().__init__(id)
        self.faction_id = faction_id
        self.category = category
        self.amount = amount
    
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


class Faction(TableObject):
    abstract = False
    def __init__(
        self,
        id: int = 0,
        user_id: int = 0,
        name: str = "",
        level: int = 0
    ):
        super().__init__(id)
        self.user_id = user_id
        self.name = name
        self.level = level

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
    
    def get_worker(self, name:str) -> Worker:
        """
        해당 세력의 인구를 가져옴
        """
        cr = self._database.fetch("worker", faction_id=self.id, name=name)

        if not cr: return Worker(faction_id=self.id, name=name)
        return Worker.from_data(cr)
    
    def get_command_counter(self, category:CommandCountCategory) -> CommandCounter:
        """
        해당 세력의 명령 카운터를 가져옴
        """
        cc = self._database.fetch("CommandCounter", faction_id=self.id, category=category.value)
        if not cc: return CommandCounter(faction_id=self.id, category=category)
        return CommandCounter.from_data(cc)
