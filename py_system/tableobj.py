"""
Sql과 연동되는 데이터 클래스들
"""
import datetime
from abc import ABCMeta
from typing import Generator
from math import sqrt

from py_base.utility import sql_value, get_minus4_to_4, DATE_FORMAT
from py_base.ari_logger import ari_logger
from py_base import ari_enum
from py_base.datatype import ExtInt, AbsentValue
from py_base.dbmanager import DatabaseManager, ON_DELETE_CASCADE, ON_UPDATE_CASCADE, ON_DELETE_SET_NULL
from py_base.yamlobj import Detail, TableObjTranslator
from py_system.abstract import Column, TableObject, HasCategoryAndAmount, ExperienceAbst
from py_base.arislena_dice import D20

def form_database_from_tableobjects(database:DatabaseManager):
    """
    TableObject 객체를 상속하는 객체의 수만큼 테이블 생성하고, 테이블을 초기화
    만약 TableObject를 상속하는 객체의 데이터 형식이 기존의 데이터 형식과 다를 경우, 기존의 데이터를 유지하며 새로운 데이터 형식을 추가
    """
    
    # 데이터베이스가 저장된 폴더에 백업 파일을 생성함
    database.backup(database.file_path.parent)
    ari_logger.info("데이터베이스 백업 완료")
    
    try:
    
        for subclass_type in TableObject.__subclasses__():
            # TableObject를 상속하는 추상 클래스는 무시함
            if not subclass_type.table_name: continue
            
            # TableObject를 상속하는 객체의 테이블을 생성함 (이미 존재할 경우, 무시함)
            database.cursor.execute(subclass_type.get_create_table_query())

            # TableObject를 상속하는 객체의 데이터 형식과 main_db의 데이터 형식을 불러와 차이를 판별하기
            # main_db의 데이터 형식을 불러옴
            db_columns = database.get_table_column_set(subclass_type.table_name)

            # TableObject를 상속하는 객체의 데이터 형식을 불러옴
            code_columns = set(subclass_type.get_columns().keys())

            # 데이터베이스 테이블의 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교
            
            # 컬럼 추가
            for column_name in (code_columns - db_columns):
                sql_type = subclass_type.get_column_type(column_name)
                default_value = sql_value(getattr(subclass_type, column_name))
                database.cursor.execute(
                    f"ALTER TABLE {subclass_type.table_name} ADD COLUMN {column_name} {sql_type} DEFAULT {default_value}"
                )
            
            # 컬럼을 제거해야 할 때, 대신 경고 발생
            for column_name in (db_columns - code_columns):
                # SQLite는 컬럼 삭제를 지원하지 않기 때문에, 삭제가 필요하면 새 테이블을 생성해야 함
                ari_logger.warning(f"{subclass_type.table_name} 테이블의 {column_name} 컬럼이 코드에 존재하지 않습니다.")
        
        # 데이터베이스에 존재하지 않는 테이블을 삭제함
        existing_tables: set[str] = database.get_all_table_names()
        tableobj_tables: set[str] = {subclass_type.table_name for subclass_type in TableObject.__subclasses__()}
        
        for table in (existing_tables - tableobj_tables):
            database.cursor.execute(f"DROP TABLE {table}")
            ari_logger.info(f"{table} 테이블이 삭제되었습니다.")
        
        database.connection.commit()
    
        ari_logger.info("데이터베이스 초기화 완료")
    
    except Exception as e:
        ari_logger.error(f"데이터베이스 초기화 실패: {e}; {e.__traceback__}")
        raise e

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
    test_mode = Column(bool, not_null=True, default=True)
    admin_mode = Column(bool, not_null=True, default=False)
    start_date = Column(str, not_null=True, default=(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_FORMAT))
    end_date = Column(str, not_null=True, default="")
    now_turn = Column(int, not_null=True, default=0)
    turn_limit = Column(int, not_null=True, default=9999)
    schedule_state = Column(ari_enum.ScheduleState, not_null=True, default=ari_enum.ScheduleState.WAITING)
    
    def __init__(
        self,
        id: int = 1,
        test_mode: bool | AbsentValue = AbsentValue(),
        admin_mode: bool | AbsentValue = AbsentValue(),
        start_date: str | AbsentValue = AbsentValue(),
        end_date: str | AbsentValue = AbsentValue(),
        now_turn: int | AbsentValue = AbsentValue(),
        turn_limit: int | AbsentValue = AbsentValue(),
        schedule_state: ari_enum.ScheduleState | AbsentValue = AbsentValue()
    ):
        super().__init__()
        self.id = id
        self.test_mode = test_mode
        self.admin_mode = admin_mode
        self.start_date = start_date
        self.end_date = end_date
        self.now_turn = now_turn
        self.turn_limit = turn_limit
        self.schedule_state = schedule_state

class JobSetting(SingleComponentTable, TableObject):
    
    table_name = "__JobSetting__"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    trigger = Column(str, not_null=True, default="cron")
    day_of_week = Column(str, not_null=True, default="mon, tue, wed, thu, fri, sat, sun")
    hour = Column(str, not_null=True, default="21")
    minute = Column(str, not_null=True, default="00")
    
    def __init__(
        self,
        id: int = 1,
        trigger: str | AbsentValue = AbsentValue(),
        day_of_week: str | AbsentValue = AbsentValue(),
        hour: str | AbsentValue = AbsentValue(),
        minute: str | AbsentValue = AbsentValue()
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
        announce_channel_id: int | None = None,
        user_role_id: int | None = None,
        admin_role_id: int | None = None
    ):
        super().__init__()
        self.id = id
        self.announce_channel_id = announce_channel_id
        self.user_role_id = user_role_id
        self.admin_role_id = admin_role_id

class User(TableObject):
    
    table_name = "User"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    discord_id = Column(int, not_null=True)
    discord_name = Column(str, not_null=True)
    register_date = Column(str, not_null=True)
    
    def __init__(
        self, 
        id: int,
        discord_id: int, 
        discord_name: str, 
        register_date: str
    ):
        super().__init__()
        self.id = id
        self.discord_id = discord_id
        self.discord_name = discord_name
        self.register_date = register_date
    
    def get_display_string(self) -> str:
        return str(self.discord_name)

class Team(TableObject):
    
    table_name = "Team"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    name = Column(str)
    
    def __init__(
        self,
        id: int,
        name: str
    ):
        super().__init__()
        self.id = id
        self.name = name

class Faction(TableObject):
    
    table_name = "Faction"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    user_id = Column(
        int, show_front=False, 
        referenced_table=User.table_name, 
        referenced_column=User.id.name,
        foreign_key_options=[ON_DELETE_CASCADE, ON_UPDATE_CASCADE]
    )
    team_id = Column(
        int, show_front=False,
        referenced_table=Team.table_name,
        referenced_column=Team.id.name,
        foreign_key_options=[ON_DELETE_SET_NULL, ON_UPDATE_CASCADE]
    )
    name = Column(str)
    
    def __init__(
        self,
        id: int = 0,
        user_id: int = 0,
        team_id: int = 0,
        name: str = ""
    ):
        super().__init__()
        self.id = id
        self.user_id = user_id
        self.team_id = team_id
        self.name = name
        
    def new(self, user_id: int, name: str, team_id: int = 1):
        return Faction(user_id=user_id, name=name, team_id=team_id)

    def get_display_string(self) -> str:
        return self.name
    
    def get_resource(self, category:ari_enum.ResourceCategory) -> "Resource":
        """
        해당 세력의 자원을 가져옴
        """
        r = self._database.fetch("resource", faction_id=self.id, category=category.value)
        if not r: return Resource(faction_id=self.id, category=category)
        return Resource.from_data(r)
    
    def get_worker(self, name:str) -> "Crew":
        """
        해당 세력의 인구를 가져옴
        """
        worker = self._database.fetch("worker", faction_id=self.id, name=name)

        if not worker: return Crew(faction_id=self.id, name=name)
        return Crew.from_data(worker)
    
    def get_command_counter(self, category:ari_enum.CommandCategory) -> "CommandCounter":
        """
        해당 세력의 명령 카운터를 가져옴
        """
        self._check_database()
        cc = self._database.fetch(CommandCounter.table_name, faction_id=self.id, category=category.value)
        if not cc: return CommandCounter(faction_id=self.id, category=category)
        return CommandCounter.from_data(cc)


    
class CommandCounter(TableObject):
    
    table_name = "CommandCounter"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(
        int, show_front=False,
        referenced_table=Faction.table_name,
        referenced_column=Faction.id.name,
        foreign_key_options=[ON_DELETE_CASCADE, ON_UPDATE_CASCADE]
    )
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

class Resource(HasCategoryAndAmount, TableObject):
    
    table_name = "Resource"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(
        int, show_front=False, 
        referenced_table=Faction.table_name,
        referenced_column=Faction.id.name,
        foreign_key_options=[ON_DELETE_SET_NULL, ON_UPDATE_CASCADE]
    )
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
        HasCategoryAndAmount.__init__(self, category, amount)
        self.id = id
        self.faction_id = faction_id
        self.category = category
        self.amount = amount
    
    def get_display_string(self) -> str:
        return self.category.local_name
    
    def to_embed_value(self) -> str:
        return f"- {self.category.express()} : {self.amount}"
    
    def is_afford(self, amount: int) -> bool:
        return self.amount >= amount

class Crew(TableObject):
    
    table_name = "Crew"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(
        int, show_front=False, 
        referenced_table=Faction.table_name, 
        referenced_column=Faction.id.name,
        foreign_key_options=[ON_DELETE_SET_NULL, ON_UPDATE_CASCADE]
    )
    name = Column(str)
    bio_sex = Column(ari_enum.BiologicalSex)
    efficiency = Column(int)
    hp = Column(int)
    availability = Column(ari_enum.Availability)
    
    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        name: str = "",
        bio_sex: ari_enum.BiologicalSex = ari_enum.BiologicalSex.UNSET,
        efficiency: int = 0,
        hp: int = 0,
        availability: ari_enum.Availability = ari_enum.Availability.UNAVAILABLE,
    ):
        TableObject.__init__(self)
        self.id = id
        self.faction_id = faction_id
        self.name = name
        self.bio_sex = bio_sex
        self.efficiency = efficiency
        self.hp = hp
        self.availability = availability
        
        self._efficiency_dice = None
        self._stats: WorkerStats = None
        self._description: WorkerDescription = None
        self._experience: dict[ari_enum.ExperienceCategory, WorkerExperience] = {}
        
    @property
    def stats(self) -> "WorkerStats":
        return self._stats
        
    @property
    def description(self) -> "WorkerDescription":
        return self._description
        
    @property
    def experience(self) -> dict[ari_enum.ExperienceCategory, "WorkerExperience"]:
        return self._experience
    
    def store_stats(self):
        self._check_database()
        self._stats = WorkerStats.from_database(self._database, worker_id=self.id)
    
    def store_description(self):
        self._check_database()
        desc = WorkerDescription.from_data(self._database.fetch(WorkerDescription.table_name, worker_id=self.id))
        if desc.worker_id != self.id: desc.worker_id = self.id
        self._description = desc
    
    def store_experience(self):
        self._check_database()
        for category in ari_enum.ExperienceCategory.to_list():
            we = WorkerExperience.from_database(self._database, worker_id=self.id, category=category)
            self._experience[category] = we

    def set_efficiency(self):
        # -4 ~ 4
        self.efficiency = get_minus4_to_4()
        return self
    
    def get_experience(self, category: ari_enum.ExperienceCategory) -> "WorkerExperience":
        self._check_database()
        we = WorkerExperience.from_database(
            self._database, worker_id=self.id, category=category
        )
        return we
    
    def is_available(self) -> bool:
        return self.availability.is_available()
    
    def recover_hp(self, amount: int):
        if not self.stats: self.store_stats()
        self.hp = min(self.hp + amount, self.stats.max_hp)

class WorkerExperience(ExperienceAbst, TableObject):
    
    table_name = "WorkerExperience"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    worker_id = Column(
        int, show_front=False, 
        referenced_table=Crew.table_name, 
        referenced_column=Crew.id.name,
        foreign_key_options=[ON_DELETE_CASCADE, ON_UPDATE_CASCADE]
    )
    category = Column(ari_enum.ExperienceCategory)
    amount = Column(int)
    
    def __init__(
        self,
        id: int = 0,
        worker_id: int = 0,
        category: ari_enum.ExperienceCategory = ari_enum.ExperienceCategory.UNSET,
        amount: int = 0
    ):
        TableObject.__init__(self)
        ExperienceAbst.__init__(self, category, amount)
        self.id = id
        self.worker_id = worker_id
        self.category = category
        self.amount = amount

    def __int__(self):
        return self.amount
        
    @classmethod
    def new(cls, worker_id: int, category: ari_enum.ExperienceCategory):
        return cls(worker_id=worker_id, category=category)
    
    def get_display_string(self) -> str:
        return self.category.local_name
    
    def to_embed_value(self) -> str:
        return f"- {self.category.express()} : {self.amount}"

class WorkerDescription(TableObject):
    
    table_name = "WorkerDescription"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    worker_id = Column(
        int, show_front=False,
        referenced_table=Crew.table_name,
        referenced_column=Crew.id.name,
        foreign_key_options=[ON_DELETE_CASCADE, ON_UPDATE_CASCADE]
    )
    worker_efficiency_detail = Column(str)
    ps_0 = Column(str)
    ps_1 = Column(str)
    ps_2 = Column(str)
    
    def __init__(
        self,
        id: int = 0,
        worker_id: int = 0,
        worker_efficiency_detail: str = "",
        ps_0: str = "",
        ps_1: str = "",
        ps_2: str = ""
    ):
        TableObject.__init__(self)
        self.id = id
        self.worker_id = worker_id
        self.worker_efficiency_detail = worker_efficiency_detail
        self.ps_0 = ps_0
        self.ps_1 = ps_1
        self.ps_2 = ps_2
    
    @classmethod
    def new(cls, worker_id: int, file: Detail):
        desc = file.get_random_worker_descriptions(3)
        return cls(worker_id=worker_id, ps_0=desc[0], ps_1=desc[1], ps_2=desc[2])
    
    def set_worker_efficiency_detail(self, d20_judge_name: str, file:Detail):
        self.worker_efficiency_detail = file.get_random_detail(d20_judge_name)
        return self
    
    def get_display_string(self) -> str:
        return self.worker_id
    
    def get_description_line(self) -> str:
        return f"**{self.ps_0}** | **{self.ps_1}** | **{self.ps_2}**"
    
    def to_embed_value(self, translator: TableObjTranslator) -> str:
        lines = [
            f"- {translator.get(self.__class__.worker_efficiency_detail.name, self.table_name)} : **{self.worker_efficiency_detail}**",
            f"- 특징: {self.get_description_line()}"
        ]
        return "\n".join(lines)

class WorkerStats(TableObject):
    
    table_name = "WorkerStats"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    worker_id = Column(
        int, show_front=False,
        referenced_table=Crew.table_name,
        referenced_column=Crew.id.name,
        foreign_key_options=[ON_DELETE_CASCADE, ON_UPDATE_CASCADE]
    )
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

class Territory(TableObject):
    
    table_name = "Territory"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(
        int, show_front=False,
        referenced_table=Faction.table_name,
        referenced_column=Faction.id.name,
        foreign_key_options=[ON_DELETE_SET_NULL, ON_UPDATE_CASCADE]
    )
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

class Facility(TableObject):
    
    table_name = "Facility"
    facility_category: ari_enum.FacilityCategory = ari_enum.FacilityCategory.UNSET

    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    faction_id = Column(
        int, show_front=False,
        referenced_table=Faction.table_name,
        referenced_column=Faction.id.name,
        foreign_key_options=[ON_DELETE_SET_NULL, ON_UPDATE_CASCADE]
    )
    territory_id = Column(
        int, show_front=False,
        referenced_table=Territory.table_name,
        referenced_column=Territory.id.name,
        foreign_key_options=[ON_DELETE_SET_NULL, ON_UPDATE_CASCADE]
    )
    category = Column(ari_enum.FacilityCategory)
    name = Column(str)
    remaining_cost = Column(int)
    level = Column(int)
    shared = Column(bool)

    def __init__(
        self,
        id: int = 0,
        faction_id: int = 0,
        territory_id: int = 0,
        category: ari_enum.FacilityCategory = ari_enum.FacilityCategory.UNSET,
        name: str = "",
        remaining_cost: int = 0,
        level: int = 0,
        shared: bool = True
    ):
        super().__init__()
        self.id = id
        self.faction_id = faction_id
        self.territory_id = territory_id
        self.category = category
        self.name = name
        self.remaining_cost = remaining_cost
        self.level = level
        self.shared = shared
        
    @property
    def deploy_limit(self) -> int:
        raise NotImplementedError()
        
    @property
    def production_requirement(self) -> int:
        raise NotImplementedError()

    def get_display_string(self) -> str:
        return f"{self.name}: {self.category.express()}"


class Deployment(TableObject):
    
    table_name = "Deployment"
    
    id = Column(int, show_front=False, primary_key=True, auto_increment=True)
    worker_id = Column(
        int, referenced_table=Crew.table_name, 
        referenced_column=Crew.id.name,
        foreign_key_options=[ON_DELETE_CASCADE, ON_UPDATE_CASCADE]
    )
    territory_id = Column(
        int, referenced_table=Territory.table_name, 
        referenced_column=Faction.id.name,
        foreign_key_options=[ON_DELETE_CASCADE, ON_UPDATE_CASCADE]
    )
    facility_id = Column(
        int, referenced_table=Facility.table_name, 
        referenced_column=Facility.id.name,
        foreign_key_options=[ON_DELETE_CASCADE, ON_UPDATE_CASCADE]
    )
    deploy_as = Column(ari_enum.DeployAs)
    
    def __init__(
        self,
        id: int = 0,
        worker_id: int = -1,
        territory_id: int = -1,
        facility_id: int = -1,
        deploy_as: ari_enum.DeployAs = ari_enum.DeployAs.WORKER
    ):
        super().__init__()
        self.id = id
        self.worker_id = worker_id
        self.territory_id = territory_id
        self.facility_id = facility_id
        self.deploy_as = deploy_as
    
    def get_display_string(self) -> str:
        return f"배치 현황 {self.id}"
    
    def get_worker(self) -> Crew:
        """
        배치된 인원을 가져옴
        """
        self._check_database()
        return Crew.from_data(self._database.fetch(Crew.table_name, id=self.worker_id))

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


class Command(TableObject):
    
    # TODO
    

