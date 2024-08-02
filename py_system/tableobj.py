"""
Sql과 연동되는 데이터 클래스들
"""
import datetime
from abc import ABCMeta
from sqlite3 import Row
from typing import Generator

from py_base.utility import sql_value, DATE_EXPR
from py_base.ari_logger import ari_logger
from py_base import ari_enum
from py_base.datatype import ExtInt
from py_base.dbmanager import DatabaseManager
from py_base.yamlobj import Detail, TableObjTranslator
from py_system.abstract import Column, TableObject, ResourceAbst, GeneralResource
from py_base.arislena_dice import D20

def form_database_from_tableobjects(database:DatabaseManager):
    """
    TableObject 객체를 상속하는 객체의 수만큼 테이블 생성하고, 테이블을 초기화
    만약 TableObject를 상속하는 객체의 데이터 형식이 기존의 데이터 형식과 다를 경우, 기존의 데이터를 유지하며 새로운 데이터 형식을 추가
    """
    
    for subclass_type in TableObject.__subclasses__():
        # TableObject를 상속하는 추상 클래스는 무시함
        if not subclass_type.table_name: continue
        # TableObject를 상속하는 객체의 테이블을 생성함 (이미 존재할 경우, 무시함)
        subclass = subclass_type()
        subclass.set_database(database)
        database.cursor.execute(subclass.get_create_table_string())

        # TableObject를 상속하는 객체의 데이터 형식과 main_db의 데이터 형식을 불러와 차이를 판별하기
        # main_db의 데이터 형식을 불러옴
        sql_table_column_set = database.table_column_set(subclass.table_name)

        # TableObject를 상속하는 객체의 데이터 형식을 불러옴
        tableobj_column_set = set(subclass.get_dict().keys())

        # 데이터베이스 테이블의 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교함
        # TableObject를 상속하는 객체에 없는 데이터 형식이 있을 경우, main_db에서 해당 데이터 형식을 삭제함
        for column_name in (sql_table_column_set - tableobj_column_set):
            database.cursor.execute(f"ALTER TABLE {subclass.table_name} DROP COLUMN {column_name}")
        # main_db에 없는 데이터 형식이 있을 경우, main_db에 해당 데이터 형식을 추가하고, 기본값을 넣음
        # subclass 객체는 기본값을 가지고 있다는 점을 이용함
        for column_name in (tableobj_column_set - sql_table_column_set):
            database.cursor.execute(
                f"ALTER TABLE {subclass.table_name} ADD COLUMN {column_name} {subclass.get_column_type(column_name)} DEFAULT {sql_value(getattr(subclass, column_name))}"
            )
    
    # 데이터베이스의 테이블 목록 불러오기
    database.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables: set[str] = {table[0] for table in database.cursor.fetchall()}
    tables.remove("sqlite_sequence")
    # TableObject를 상속하는 객체의 테이블 목록 불러오기
    tableobj_tables: set[str] = {subclass().table_name for subclass in TableObject.__subclasses__()}
    
    # 데이터베이스에 존재하지 않는 테이블을 삭제함
    for table in (tables - tableobj_tables):
        database.cursor.execute(f"DROP TABLE {table}")
        
    # Schedule 테이블에 요소가 없을 경우, 새 요소를 추가함
    for single_component_table in SingleComponentTable.__subclasses__():
        if not database.fetch(single_component_table.table_name, id=1):
            single_component_table().set_database(database).push()
    
    database.connection.commit()
    
    ari_logger.info("Database initialized")

class Inventory(metaclass=ABCMeta):
    """
    인벤토리처럼 활용되는 객체
    """
    # TODO

class SingleComponentTable(TableObject, metaclass=ABCMeta):
    
    def __init__(self, id: int = 1):
        super().__init__()
    
    @classmethod
    def from_database(cls, database: DatabaseManager):
        return super().from_database(database, id=1)
    
    def get_display_string(self) -> str:
        return ""

"""
액티브 데이터
"""

class Chalkboard(SingleComponentTable, TableObject):
    
    table_name = "__Chalkboard__"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    test_mode = Column(bool)
    admin_mode = Column(bool)
    start_date = Column(str)
    end_date = Column(str)
    now_turn = Column(int)
    turn_limit = Column(int)
    state = Column(ari_enum.ScheduleState)
    
    def __init__(
        self,
        id: int = 1,
        test_mode: bool = True,
        admin_mode: bool = False,
        start_date: str = (datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPR),
        end_date: str = "",
        now_turn: int = 0,
        turn_limit: int = 9999,
        state: ari_enum.ScheduleState = ari_enum.ScheduleState.WAITING
    ):
        super().__init__()
        self.id = id
        self.test_mode = test_mode
        self.admin_mode = admin_mode
        self.start_date = start_date
        self.end_date = end_date
        self.now_turn = now_turn
        self.turn_limit = turn_limit
        self.state = state

class JobSetting(SingleComponentTable, TableObject):
    
    table_name = "__JobSetting__"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    trigger = Column(str)
    day_of_week = Column(str)
    hour = Column(str)
    minute = Column(str)
    
    def __init__(
        self,
        id: int = 1,
        trigger: str = "cron",
        day_of_week: str = "mon, tue, wed, thu, fri, sat, sun",
        hour: str = "21",
        minute: str = "00"
    ):
        super().__init__()
        self.id = id
        self.trigger = trigger
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute

class GuildSetting(SingleComponentTable, TableObject):
    
    table_name = "__GuildSetting__"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    announce_channel_id = Column(int)
    user_role_id = Column(int)
    admin_role_id = Column(int)
    
    def __init__(
        self,
        id: int = 1,
        announce_channel_id: int = 0,
        user_role_id: int = 0,
        admin_role_id: int = 0
    ):
        super().__init__()
        self.id = id
        self.announce_channel_id = announce_channel_id
        self.user_role_id = user_role_id
        self.admin_role_id = admin_role_id

class User(TableObject):
    
    table_name = "User"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    discord_id = Column(int)
    discord_name = Column(str)
    register_date = Column(str)
    
    def __init__(
        self, 
        id: int = 0,
        discord_id: int = 0, 
        discord_name: str = "", 
        register_date: str = ""
    ):
        super().__init__()
        self.id = id
        self.discord_id = discord_id
        self.discord_name = discord_name
        self.register_date = register_date
    
    def get_display_string(self) -> str:
        return str(self.discord_name)


class Resource(TableObject, ResourceAbst):
    
    table_name = "Resource"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(int, show_front=False)
    category = Column(ari_enum.ResourceCategory)
    amount = Column(ExtInt)
    
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        category: ari_enum.ResourceCategory = ari_enum.ResourceCategory.UNSET,
        amount: ExtInt | int = ExtInt(0, min_value=0)
    ):
        if type(amount) == int:
            amount = ExtInt(amount, min_value=0)
        TableObject.__init__(self)
        ResourceAbst.__init__(self, category, amount)
        self.id = id
        self.faction_id = faction_id
        self.category = category
        self.amount = amount
    
    def get_display_string(self) -> str:
        return self.category.local_name
    
    def to_embed_value(self) -> str:
        return f"- {self.category.express()} : {self.amount}"

class WorkerExperience(TableObject):
    
    table_name = "WorkerExperience"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    worker_id = Column(int, show_front=False)
    category = Column(ari_enum.WorkCategory)
    experience = Column(int)
    
    def __init__(
        self,
        id: int = 0,
        worker_id: int = 0,
        category: ari_enum.WorkCategory = ari_enum.WorkCategory.UNSET,
        experience: int = 0
    ):
        TableObject.__init__(self)
        self.id = id
        self.worker_id = worker_id
        self.category = category
        self.experience = experience

    def __int__(self):
        return self.experience
        
    @classmethod
    def new(cls, worker_id: int, category: ari_enum.WorkCategory):
        return cls(worker_id=worker_id, category=category)
    
    def get_display_string(self) -> str:
        return self.category.local_name
    
    def to_embed_value(self) -> str:
        return f"- {self.category.express()} : {self.experience}"

class WorkerDescription(TableObject):
    
    table_name = "WorkerDescription"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    worker_id = Column(int, show_front=False)
    worker_labor_detail = Column(str)
    ps_0 = Column(str)
    ps_1 = Column(str)
    ps_2 = Column(str)
    
    def __init__(
        self,
        id: int = 0,
        worker_id: int = 0,
        worker_labor_detail: str = "",
        ps_0: str = "",
        ps_1: str = "",
        ps_2: str = ""
    ):
        TableObject.__init__(self)
        self.id = id
        self.worker_id = worker_id
        self.worker_labor_detail = worker_labor_detail
        self.ps_0 = ps_0
        self.ps_1 = ps_1
        self.ps_2 = ps_2
    
    @classmethod
    def new(cls, worker_id: int, file: Detail):
        desc = file.get_random_worker_descriptions(3)
        return cls(worker_id=worker_id, ps_0=desc[0], ps_1=desc[1], ps_2=desc[2])
    
    def set_worker_labor_detail(self, d20_judge_name: str, file:Detail):
        self.worker_labor_detail = file.get_random_detail(d20_judge_name)
        return self
    
    def get_display_string(self) -> str:
        return self.worker_id
    
    def get_description_line(self) -> str:
        return f"**{self.ps_0}** | **{self.ps_1}** | **{self.ps_2}**"
    
    def to_embed_value(self, translator: TableObjTranslator) -> str:
        lines = [
            f"- {translator.get(self.__class__.worker_labor_detail.name, self.table_name)} : **{self.worker_labor_detail}**",
            f"- 특징: {self.get_description_line()}"
        ]
        return "\n".join(lines)

class WorkerStats(TableObject):
    
    table_name = "WorkerStats"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    worker_id = Column(int, show_front=False)
    max_hp = Column(int)
    
    def __init__(
        self,
        id: int = 0,
        worker_id: int = 0,
        max_hp: int = 0
    ):
        TableObject.__init__(self)
        self.id = id
        self.worker_id = worker_id
        self.max_hp = max_hp
        
    def get_display_string(self) -> str:
        return super().get_display_string()

class Worker(TableObject):
    
    table_name = "Worker"
    correspond_category: ari_enum.WorkerCategory = None
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(int, show_front=False)
    category = Column(ari_enum.WorkerCategory)
    name = Column(str)
    sex = Column(ari_enum.BiologicalSex)
    labor = Column(int)
    hp = Column(int)
    availability = Column(ari_enum.Availability)
    
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        category: ari_enum.WorkerCategory = ari_enum.WorkerCategory.UNSET,
        name: str = "",
        sex: ari_enum.BiologicalSex = ari_enum.BiologicalSex.UNSET,
        labor: int = 0,
        hp: int = 0,
        availability: ari_enum.Availability = ari_enum.Availability.UNAVAILABLE,
    ):
        TableObject.__init__(self)
        self.id = id
        self.faction_id = faction_id
        self.category = category
        self.name = name
        self.sex = sex
        self.labor = labor
        self.hp = hp
        self.availability = availability
        
        self._labor_dice = None
    
    def get_display_string(self) -> str:
        return self.name
    
    def get_experience_level(self, worker_exp: WorkerExperience) -> int:
        raise NotImplementedError()

    def get_consumption_recipe(self) -> list[GeneralResource]:
        """
        노동력 소모에 필요한 자원을 반환함
        """
        raise NotImplementedError()

    def set_labor(self):
        raise NotImplementedError()
    
    def get_experience(self, category: ari_enum.WorkCategory) -> WorkerExperience:
        self._check_database()
        we = WorkerExperience.from_database(
            self._database, worker_id=self.id, category=category
        )
        return we
    
    def get_labor_by_WorkCategory(self, category: ari_enum.WorkCategory) -> int:
        return self.labor + self.get_experience_level(self.get_experience(category))
    
    def set_labor_dice(self) -> D20:
        """
        experience 수치에 따라 주사위의 modifier가 다르게 설정됨
        """
        self._labor_dice = D20()
        return self
    
    def set_description(self):
        self._check_database()
        self.description = WorkerDescription.from_database(self._database, worker_id=self.id)
        return self
    
    def set_stats(self):
        self._check_database()
        self.stats = WorkerStats.from_database(self._database, worker_id=self.id)
        return self
    
    def is_available(self) -> bool:
        return self.availability.is_available()
    
class FactionHierarchyNode(TableObject):
    
    table_name = "FactionHierarchyNode"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    higher = Column(int)
    lower = Column(int)
    
    def __init__(
        self,
        id: int = 0,
        higher: int = 0,
        lower: int = 0
    ):
        super().__init__()
        self.id = id
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


class Facility(TableObject):
    
    table_name = "Facility"
    facility_category = ari_enum.FacilityCategory.UNSET
    required_dice_cost: int = 0

    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(int, show_front=False)
    territory_id = Column(int, show_front=False)
    category = Column(ari_enum.FacilityCategory)
    name = Column(str)
    remaining_dice_cost = Column(int)
    level = Column(int)
    shared = Column(bool)

    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        territory_id: int = 0,
        category: ari_enum.FacilityCategory = ari_enum.FacilityCategory.UNSET,
        name: str = "",
        remaining_dice_cost: int = 0,
        level: int = 0,
        shared: bool = True
    ):
        super().__init__()
        self.id = id
        self.faction_id = faction_id
        self.territory_id = territory_id
        self.category = category
        self.name = name
        self.remaining_dice_cost = remaining_dice_cost
        self.level = level
        self.shared = shared

    @property
    def deploy_limit(self) -> int:
        return self.level + 2

    def get_display_string(self) -> str:
        return f"{self.name}: {self.category.express()}"

    def is_deployable(self, deployed_worker_ids: list[int] | None = None) -> bool:
        if not self.is_built(): return True

        if deployed_worker_ids is None:
            deployed_worker_ids = self.get_deployed_worker_ids()

        if len(deployed_worker_ids) >= self.deploy_limit: return False
        return True

    def deploy(self, worker: Worker):
        """
        시설에 인원 배치

        시설 완공 여부, 시설 배치 인원 제한 여부, 이미 배치된 인원 여부를 확인함

        이전 배치 정보가 존재하는 경우 삭제
        """
        self._check_database()
        if not self.is_deployable():
            ari_logger.warning(
                "이 경고가 발생했다면 코드를 수정하세요 - 시설에 더 이상 인원을 배치할 수 없습니다. (최대 수용량에 다다름)"
            )
            return
        self._database.connection.execute(
            f"DELETE FROM Deployment WHERE worker_id = {worker.id}"
        )
        deployment = Deployment(worker_id=worker.id, territory_id=self.territory_id, facility_id=self.id)
        deployment.set_database(self._database)
        deployment.push()

    def apply_production(self, dice:int):
        if self.is_built():
            raise ValueError("시설이 완공되었습니다.")
        self.remaining_dice_cost = max(0, self.remaining_dice_cost - dice)

    def is_built(self) -> bool:
        """
        시설이 완공되었는지 확인
        """
        return self.remaining_dice_cost == 0

    def get_deployed_worker_ids(self) -> list[int]:
        """
        시설에 배치된 인원의 ID를 가져옴

        ! database가 필요함
        """
        self._check_database()
        ids:list[Row] = self._database.cursor.execute("SELECT worker_id FROM deployment WHERE facility_id = ?", (self.id,)).fetchall()
        return [id[0] for id in ids]

    def get_deployed_workers(self, deployment_list: list["Deployment"]) -> list[Worker]:
        """
        시설에 배치된 인원을 가져옴

        ! database가 필요함
        """
        self._check_database()
        return [deployment.get_worker() for deployment in deployment_list if deployment.worker_id is not None]

    def get_production_recipe(self):
        raise NotImplementedError()
    
    @classmethod
    def get_matched_subclass_from_category(cls, category: ari_enum.FacilityCategory) -> type["Facility"]:
        for subcls in cls.__class__.__subclasses__():
            if subcls.facility_category == category:
                return subcls
        raise ValueError("카테고리에 해당하는 하위 시설이 없습니다! 코드를 확인해주세요.")

class Territory(TableObject):
    
    table_name = "Territory"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(int, show_front=False)
    name = Column(str)
    space_limit = Column(int)
    safety = Column(ari_enum.TerritorySafety)
    shared = Column(bool)
    
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        name: str = "",
        space_limit: int = 3,
        safety: ari_enum.TerritorySafety = ari_enum.TerritorySafety.UNKNOWN,
        shared: bool = True
    ):
        super().__init__()
        self.id = id
        self.faction_id = faction_id
        self.name = name
        self.space_limit = space_limit
        self.safety = safety
        self.shared = shared
        
    @classmethod
    def new(cls, faction_id:int, name:str):
        new_instance = cls(faction_id=faction_id, name=name)\
            .set_safety_by_random()
        return new_instance

    def get_display_string(self) -> str:
        return self.name

    def set_safety_by_random(self):
        """
        안전도를 랜덤으로 설정함
        """
        if self.safety == ari_enum.TerritorySafety.UNKNOWN:
            self.safety = ari_enum.TerritorySafety.get_randomly()
        return self
    
    def get_remaining_space(self) -> int:
        """
        남은 공간
        """
        return self.space_limit - len(self._database.fetch_many(Facility.table_name, territory_id=self.id))


class Deployment(TableObject):
    
    table_name = "Deployment"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    worker_id = Column(int)
    territory_id = Column(int)
    facility_id = Column(int)
    
    def __init__(
        self,
        id: int = 0,
        worker_id: int = -1,
        territory_id: int = -1,
        facility_id: int = -1
    ):
        super().__init__()
        self.id = id
        self.worker_id = worker_id
        self.territory_id = territory_id
        self.facility_id = facility_id
    
    def get_display_string(self) -> str:
        return f"배치 현황 {self.id}"
    
    def get_worker(self) -> Worker:
        """
        배치된 인원을 가져옴
        """
        self._check_database()
        return Worker.from_data(self._database.fetch(Worker.table_name, id=self.worker_id))

    def get_facility(self) -> "Facility":
        """
        배치된 시설을 가져옴
        """
        self._check_database()
        return Facility.from_data(self._database.fetch(Facility.table_name, id=self.facility_id))
    
    @classmethod
    def get_unique_facility_ids(cls, database: DatabaseManager) -> Generator[int, None, None]:
        for row in database.cursor.execute(f"SELECT DISTINCT {cls.facility_id.name} FROM {cls.table_name}").fetchall():
            yield row[0]


class CommandCounter(TableObject):
    
    table_name = "CommandCounter"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(int, show_front=False)
    category = Column(ari_enum.CommandCategory)
    amount = Column(int)
    
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        category: ari_enum.CommandCategory = ari_enum.CommandCategory.UNSET,
        amount: int = 0
    ):
        super().__init__()
        self.id = id
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
    
    table_name = "Faction"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    user_id = Column(int, show_front=False)
    name = Column(str)
    level = Column(int)
    
    def __init__(
        self,
        id: int = 0,
        user_id: int = 0,
        name: str = "",
        level: int = 0
    ):
        super().__init__()
        self.id = id
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
    
    def get_resource(self, category:ari_enum.ResourceCategory) -> Resource:
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
    
    def get_command_counter(self, category:ari_enum.CommandCategory) -> CommandCounter:
        """
        해당 세력의 명령 카운터를 가져옴
        """
        self._check_database()
        cc = self._database.fetch("CommandCounter", faction_id=self.id, category=category.value)
        if not cc: return CommandCounter(faction_id=self.id, category=category)
        return CommandCounter.from_data(cc)
