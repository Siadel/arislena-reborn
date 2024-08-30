from abc import ABCMeta, abstractmethod
from typing import Self, Iterator
from sqlite3 import Row

from py_base import ari_enum, utility
from py_base.ari_enum import ExperienceCategory
from py_base.ari_logger import ari_logger
from py_system import resource, experience
from py_system.resource import GeneralResource, ProductionResource
from py_system.abstract import ConcreteObject
from py_system.tableobj import Facility, Deployment, Crew, WorkerExperience
from py_system.experience import GeneralExperience, OPTIMIZED_MIN_EXP_BY_LEVEL

class StatPerLevelConfig:
    """
    레벨에 따라 변화하는 수치를 설정하는 클래스
    """
    def __init__(
        self, 
        base : int, 
        frequency : int, 
        ratio : int = 0, 
        max_or_min : int | None = None
    ):
        self.base = base
        self.frequency = frequency
        self.ratio = ratio
        self.max_or_min = max_or_min
    
    def calculate(self, level:int) -> int:
        """
        base_limit + level이 frequency만큼 오를 때마다 ratio만큼 증가함 (최대 max_add)
        """
        return stat_per_level(
            self.base, self.frequency, self.ratio, self.max_or_min, level
        )
    

def stat_per_level(base:int, frequency:int, ratio:int, max_or_min:int|None, level:int) -> int:
    """
    레벨에 따라 변화하는 수치를 설정하는 함수
    
    base_limit + level이 frequency만큼 오를 때마다 ratio만큼 증가함 (최대 max_add)
    """
    if frequency == 0: return base
    core = lambda x: (x // frequency) * ratio

    if max_or_min is None:
        return base + core(level)

    if ratio >= 0:
        return base + min(max_or_min, core(level))
    elif ratio < 0:
        return base + max(max_or_min, core(level))

class ConcreteFacility(ConcreteObject, Facility, metaclass=ABCMeta):
    """
    FacilityBase 하위 클래스들의 부모 클래스
    """
    corresponding_category: ari_enum.FacilityCategory = ari_enum.FacilityCategory.UNSET
    deploy_as_worker_limit_config: StatPerLevelConfig = StatPerLevelConfig(0, 0, 0, 0)
    deploy_as_visitor_limit_config: StatPerLevelConfig = StatPerLevelConfig(0, 0, 0, 0)
    require_headquarter_level: int = 0
    construction_cost: int = 0
    level_up_cost_config: StatPerLevelConfig = StatPerLevelConfig(0, 0, 0, 0)
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
        
    @property
    def deploy_limit(self) -> int:
        """
        시설이 배치될 수 있는 최대 수
        """
        return self.deploy_as_worker_limit_config.calculate(self.level)
    
    @property
    def level_up_cost(self) -> int:
        return self.level_up_cost_config.calculate(self.level)
    
    @abstractmethod
    def get_production_by_itself(self) -> list[GeneralResource]:
        """
        시설 자체에서 생산하는 자원 목록을 반환함
        """
        return []
    
    @abstractmethod
    def get_production_by_worker(self) -> list[ProductionResource]:
        """
        대원을 통해 생산하는 자원 목록을 반환함
        """
        return []
    
    @abstractmethod
    def get_comsumption_by_itself(self) -> list[GeneralResource]:
        """
        자원을 생산할 때 소모되는 자원 목록을 반환함
        """
        return []
    
    @abstractmethod
    def get_consumption_by_worker(self) -> list[GeneralResource]:
        """
        대원을 통해 생산할 때 소모되는 자원 목록을 반환함
        """
        return []
    
    @abstractmethod
    def get_worker_requirements(self) -> list[GeneralExperience]:
        """
        대원이 시설에 배치될 때 요구되는 경험치 목록을 반환함
        """
        return []
    
    @abstractmethod
    def get_worker_experience_gain(self) -> list[GeneralExperience]:
        """
        배치된 대원이 얻는 경험치 목록을 반환함
        """
        return []
    
    @abstractmethod
    def on_turn_end(self):
        """
        턴 종료 시 실행되는 메서드
        """
        pass
    
    @classmethod
    def create_from(cls, facility: Facility) -> Self:
        return utility.select_from_subclasses(
            ConcreteFacility,
            corresponding_category=Facility.category
        )(facility.get_dict())

    def deploy(self, worker: Crew):
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
        self.remaining_cost = max(0, self.remaining_cost - dice)

    def is_built(self) -> bool:
        """
        시설이 완공되었는지 확인
        """
        return self.remaining_cost == 0
    
    def is_running(self) -> bool:
        """
        시설이 운영 중인지 확인
        
        조건:
        1. 완공됨
        """
        self._check_database()
        if not self.is_built(): return False
        return True
        
    def is_deployable(self, deployed_worker_ids: list[int] | None = None) -> bool:
        if not self.is_built(): return True

        if deployed_worker_ids is None:
            deployed_worker_ids = self.get_deployed_worker_ids()

        if len(deployed_worker_ids) >= self.deploy_limit: return False
        return True
    
    def get_deployed_worker_ids(self) -> list[int]:
        """
        시설에 배치된 인원의 ID를 가져옴

        ! database가 필요함
        """
        self._check_database()
        ids:list[Row] = self._database.cursor.execute("SELECT worker_id FROM deployment WHERE facility_id = ?", (self.id,)).fetchall()
        return [id[0] for id in ids]

    def get_deployments(self) -> Iterator["Deployment"]:
        """
        시설에 배치된 인원 정보를 가져옴

        ! database가 필요함
        """
        self._check_database()
        deploy_datas = self._database.cursor.execute("SELECT * FROM deployment WHERE facility_id = ?", (self.id,)).fetchall()
        return Deployment.from_data_iter(deploy_datas, self._database)

    def get_deployed_workers(self, deployment_list: list["Deployment"] | None = None) -> list[Crew]:
        """
        시설에 배치된 인원을 가져옴

        ! database가 필요함
        """
        self._check_database()
        if deployment_list is None:
            deployment_list = self.get_deployments()
        return [deployment.get_worker() for deployment in deployment_list if deployment.worker_id is not None]

class Headquarter(ConcreteFacility):
    
    corresponding_category = ari_enum.FacilityCategory.HEADQUARTER
    deploy_as_worker_limit_config = StatPerLevelConfig(1, 2, 1)
    deploy_as_visitor_limit_config = StatPerLevelConfig(0, 0)
    require_headquarter_level = 0
    construction_cost = 100
    level_up_cost_config = StatPerLevelConfig(80, 1, 30)
    
    def __init__(self, **kwargs):
        ConcreteFacility.__init__(self, **kwargs)
        
    def get_production_by_itself(self) -> list[GeneralResource]:
        return [
            resource.Spades(
                stat_per_level(2, 1, 2, None, self.level)
            )
        ]

    def get_production_by_worker(self) -> list[ProductionResource]:
        return [
            resource.SpadesProduction(
                stat_per_level(2, 2, 1, None, self.level), 
                5
            )
        ]

    def get_consumption_by_itself(self) -> list[GeneralResource]:
        return [
            resource.Gold(
                stat_per_level(0, 2, 5, None, self.level)
            )
        ]
        
    def get_consumption_by_worker(self) -> list[GeneralResource]:
        return super().get_consumption_by_worker()
    
    def get_worker_requirements(self) -> list[GeneralExperience]:
        return super().get_worker_requirements()
    
    def get_worker_experience_gain(self) -> list[GeneralExperience]:
        return [
            experience.Administration(
                stat_per_level(4, 3, 4, None, self.level)
            )
        ]
    
    def on_turn_end(self):
        return super().on_turn_end()


class GatheringSite(ConcreteFacility):
    
    corresponding_category = ari_enum.FacilityCategory.GATHERING_SITE
    deploy_as_worker_limit_config = StatPerLevelConfig(3, 0)
    deploy_as_visitor_limit_config = StatPerLevelConfig(0, 0)
    require_headquarter_level = 0
    construction_cost = 70
    level_up_cost_config = StatPerLevelConfig(35, 1, 15)
    
    def __init__(self, **kwargs):
        ConcreteFacility.__init__(self, **kwargs)
        
    def get_production_by_itself(self) -> list[GeneralResource]:
        return []
    
    def get_production_by_worker(self) -> list[ProductionResource]:
        
        return [
            resource.HeartsProduction(
                3,
                stat_per_level(7, 2, -1, -3, self.level)
            ),
            resource.ClubsProduction(
                1, 
                stat_per_level(12, 2, -1, -3, self.level)
            )
        ]
    
    def get_comsumption_by_itself(self) -> list[GeneralResource]:
        return []
    
    def get_consumption_by_worker(self) -> list[GeneralResource]:
        return []
    
    def get_worker_requirements(self) -> list[GeneralExperience]:
        return []
    
    def get_worker_experience_gain(self) -> list[GeneralExperience]:
        return [
            experience.Gathering(
                stat_per_level(3, 3, 1, None, self.level)
            ),
            experience.Pharmacy(
                stat_per_level(1, 3, 1, None, self.level)
            )
        ]
    
    def on_turn_end(self):
        return super().on_turn_end()
    
class HuntingGround(ConcreteFacility):
    
    corresponding_category = ari_enum.FacilityCategory.HUNTING_GROUND
    deploy_as_worker_limit_config = StatPerLevelConfig(6, 0)
    deploy_as_visitor_limit_config = StatPerLevelConfig(0, 0)
    construction_cost = 60
    require_headquarter_level = 0
    level_up_cost_config = StatPerLevelConfig(35, 1, 15)
    
    def __init__(self, **kwargs):
        ConcreteFacility.__init__(self, **kwargs)
        
    def get_production_by_itself(self) -> list[GeneralResource]:
        return []
    
    def get_production_by_worker(self) -> list[ProductionResource]:
        return [
            resource.HeartsProduction(
                9,
                stat_per_level(16, 2, -1, -3, self.level)
            ),
            resource.DiamondsProduction(
                12,
                stat_per_level(16, 2, -1, -3, self.level)
            )
        ]
        
    def get_comsumption_by_itself(self) -> list[GeneralResource]:
        return []
    
    def get_consumption_by_worker(self) -> list[GeneralResource]:
        return []
    
    def get_worker_requirements(self) -> list[GeneralExperience]:
        return []
    
    def get_worker_experience_gain(self) -> list[GeneralExperience]:
        return [
            experience.Hunting(
                stat_per_level(3, 3, 3, None, self.level)
            ),
            experience.Combat(
                stat_per_level(1, 3, 1, None, self.level)
            )
        ]
    
    def on_turn_end(self):
        return super().on_turn_end()
    
class Habitation(ConcreteFacility):
    
    corresponding_category = ari_enum.FacilityCategory.HABITATION
    deploy_as_worker_limit_config = StatPerLevelConfig(4, 0)
    deploy_as_visitor_limit_config = StatPerLevelConfig(0, 0)
    construction_cost = 50
    require_headquarter_level = 0
    level_up_cost_config = StatPerLevelConfig(20, 1, 10)
    
    def __init__(self, **kwargs):
        ConcreteFacility.__init__(self, **kwargs)
        
    def get_production_by_itself(self) -> list[GeneralResource]:
        return [
            resource.Spades(
                stat_per_level(1, 2, 2, None, self.level)
            )
        ]
    
    def get_production_by_worker(self) -> list[ProductionResource]:
        return [
            resource.HeartsProduction(
                1,
                stat_per_level(13, 4, -1, -7, self.level)
            ),
            resource.DiamondsProduction(
                1,
                stat_per_level(13, 4, -1, -7, self.level)
            ),
            resource.ClubsProduction(
                1,
                stat_per_level(22, 4, -1, -7, self.level)
            )
        ]
        
    def get_comsumption_by_itself(self) -> list[GeneralResource]:
        return [
            resource.Diamonds(
                stat_per_level(0, 1, 1, None, self.level)
            ),
            resource.Hearts(
                stat_per_level(0, 2, 1, None, self.level)
            ),
            resource.Clubs(
                stat_per_level(0, 6, 2, None, self.level)
            ),
            resource.Gold(
                stat_per_level(0, 4, 3, None, self.level)
            )
        ]
    
    def get_worker_requirements(self) -> list[GeneralExperience]:
        return []
    
    def get_worker_experience_gain(self) -> list[GeneralExperience]:
        return [
            experience.Manufacturing(
                stat_per_level(2, 3, 2, None, self.level)
            )
        ]
    
    def on_turn_end(self):
        """
        배치된 대원이 턴 종료 시 체력 1 회복
        건물 레벨 6마다 1 체력 추가 회복 (최대 +2)
        """
        self._check_database()
        deployed_workers = self.get_deployed_workers()
        for worker in deployed_workers:
            worker.set_database(self._database)
            worker.recover_hp(
                stat_per_level(1, 6, 1, 3, self.level)
            )


class TrainingCamp(ConcreteFacility):
    
    corresponding_category = ari_enum.FacilityCategory.TRAINING_CAMP
    deploy_as_worker_limit_config = StatPerLevelConfig(2, 2, 1, 5)
    deploy_as_visitor_limit_config = StatPerLevelConfig(2, 2, 1, 5)
    require_headquarter_level = 1
    construction_cost = 80
    level_up_cost_config = StatPerLevelConfig(40, 1, 20)
    
    def __init__(self, **kwargs):
        ConcreteFacility.__init__(self, **kwargs)
        
    def get_production_by_itself(self) -> list[GeneralResource]:
        return []
    
    def get_production_by_worker(self) -> list[ProductionResource]:
        return [
            resource.SpadesProduction(
                1, 
                6
            )
        ]
    
    def get_comsumption_by_itself(self) -> list[GeneralResource]:
        return [
            resource.Diamonds(
                stat_per_level(1, 2, 1, None, self.level)
            ),
            resource.Gold(
                stat_per_level(0, 4, 5, None, self.level)
            )
        ]
        
    def get_consumption_by_worker(self) -> list[GeneralResource]:
        return [
            resource.Diamonds(1),
            resource.Hearts(1)
        ]
    
    def get_worker_requirements(self) -> list[GeneralExperience]:
        return [
            experience.Administration(
                OPTIMIZED_MIN_EXP_BY_LEVEL[1]
            ),
            experience.Gathering(
                OPTIMIZED_MIN_EXP_BY_LEVEL[2]
            ),
            experience.Pharmacy(
                OPTIMIZED_MIN_EXP_BY_LEVEL[1]
            )
        ]
    
    def get_worker_experience_gain(self) -> list[GeneralExperience]:
        return [
            experience.Administration(
                stat_per_level(1, 3, 1, None, self.level)
            ),
            experience.Gathering(
                stat_per_level(1, 3, 1, None, self.level)
            ),
            experience.Pharmacy(
                stat_per_level(1, 3, 1, None, self.level)
            ),
            experience.Strategy(
                stat_per_level(1, 3, 1, None, self.level)
            )
        ]
    
    def on_turn_end(self):
        return super().on_turn_end()