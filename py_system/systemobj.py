"""
table object와 연계되는 데이터 클래스, 하지만 db에 직접 저장되지 않는다.
"""
from abc import ABCMeta, abstractmethod
from typing import Type, Generator

from py_base.ari_enum import ResourceCategory, FacilityCategory, WorkCategory, WorkerCategory
from py_base.arislena_dice import D20
from py_base.dbmanager import DatabaseManager
from py_system.abstract import Column, ProductionResource, GeneralResource
from py_system.tableobj import Facility
from py_system.tableobj import WorkerDescription, Resource, Deployment, Worker, WorkerExperience, WorkerStats
from py_system.worker import Crew, Livestock



    
    
# TODO schedule_manager의 facility_produce 함수 기능을 여기로 끌어올 수 있을 텐데



# 시설


class SystemFacility(Facility, metaclass=ABCMeta):
    """
    시설 클래스들의 부모 클래스
    """
    facility_category: FacilityCategory = FacilityCategory.UNSET
    work_category: WorkCategory = WorkCategory.UNSET
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_showables(self) -> list[str]:
        return Facility.get_showables()
    
    @abstractmethod
    def get_production_recipe(self) -> ProductionRecipe:
        return ProductionRecipe()

    @classmethod
    def from_facility(cls, facility: Facility) -> "SystemFacility":
        """
        Facility 객체를 FacilityBase 하위 객체로 변환한다.
        """
        for sub_cls_type in cls.__subclasses__():
            if sub_cls_type.facility_category.value == facility.category.value:
                return sub_cls_type(**facility.get_dict())
        raise ValueError(f"해당 카테고리({facility.category})의 시설이 없습니다.")

    @classmethod
    def type_from_category(cls, category:FacilityCategory) -> Type["SystemFacility"]:
        """
        FacilityBase를 상속받은 클래스들 중에서 category에 해당하는 클래스를 반환
        """
        for sub_cls_type in cls.__subclasses__():
            if sub_cls_type.facility_category.value == category.value:
                return sub_cls_type
        raise ValueError(f"해당 카테고리({category})의 시설이 없습니다.")
    
    def produce_resource_by_worker(self, database: DatabaseManager, crew: Crew) -> Generator[Resource, None, None]:
        """
        해당 시설에서 일하는 노동 개체(대원, 가축)가 생산한 자원(Resource 객체)을 반환
        
        이 함수로 반환한 Resource 객체는 직접 database에 저장해야 한다. 단, database 등록은 되어 있다.
        """
        recipe = self.get_production_recipe()
        for produce_resource in recipe.produce:
            r_data = database.fetch(
                Resource.table_name,
                faction_id = self.faction_id,
                category = produce_resource.category.value
            )
            resource = Resource.from_data(r_data, faction_id=self.faction_id, category=produce_resource.category)
            resource.set_database(database)
            
            produced_resource = produce_resource * crew.get_experience_level(crew.get_experience(produce_resource.category))
            resource.amount += produced_resource.amount
        
            yield resource
    
    @property
    def construction_progress(self) -> int:
        return self.required_dice_cost - self.remaining_dice_cost
    
    def get_deployed_crews(self, deployment_list: list[Deployment]) -> list[Crew]:
        self._check_database()
        deployed_workers = self.get_deployed_workers(deployment_list)
        return [Crew.from_data(row).set_database(self._database) for row in deployed_workers if row.category == WorkerCategory.CREW]
    
    def get_deployed_livestocks(self, deployment_list: list[Deployment]) -> list[Livestock]:
        self._check_database()
        deployed_workers = self.get_deployed_workers(deployment_list)
        return [Livestock.from_data(row).set_database(self._database) for row in deployed_workers if row.category == WorkerCategory.LIVESTOCK]
    
    def level_up(self):
        # 여기에 warnings 객체 넣어야 하는데...
        if not self.is_built(): return
        self.remaining_dice_cost = self.level * 25 + int(self.__class__.required_dice_cost / 2)

    # def construct(self, deployed_crews: list[Crew]):
    #     if self.is_built(): return
        
    #     for crew in deployed_crews:
    #         construction_exp = crew.get_experience(LaborCategory.CONSTRUCTION)
    #         construction_dice = construction_exp.get_efficiency_dice()
    #         construction_dice.roll()
            
    #         self.apply_production(construction_dice.last_roll)




# class Reservoir(Storages):
#     category: int = 3
#     name: str = "저수지"
#     required_dice_cost: int = 70
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.WATER, 20),
#         ]
#     )


# class Granary(Storages):
#     category: int = 4
#     name: str = "곡창"
#     required_dice_cost: int = 70
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.FOOD, 20),
#             GeneralResource(ResourceCategory.FEED, 20)
#         ]
#     )


# class FacilityMaterialStorage(Storages):
#     category: int = 5
#     name: str = "건자재 창고"
#     required_dice_cost: int = 70
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource("facility_material", 20),
#         ]
#     )