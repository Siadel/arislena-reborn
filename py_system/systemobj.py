"""
table object와 연계되는 데이터 클래스, 하지만 db에 직접 저장되지 않는다.
"""
import random
from abc import ABCMeta, abstractmethod
from typing import Type, Generator

from py_base.ari_enum import ResourceCategory, BuildingCategory, WorkCategory, WorkerCategory
from py_base.arislena_dice import Dice, Nonahedron
from py_base.dbmanager import DatabaseManager
from py_system.abstract import ResourceAbst, GeneralResource, Workable
from py_system.tableobj import Building, WorkerDescription, Resource, Deployment, Worker, WorkerExperience

# TableObject 상속 클래스
class Crew(Worker, Workable):
    abstract = False
    correspond_category = WorkerCategory.CREW

    def __init__(self, **kwargs):
        Worker.__init__(self, **kwargs)
        Workable.__init__(self)

    @classmethod
    def new(cls, faction_id: int):
        """
        faction_id에 해당하는 세력에 새로운 대원을 생성함

        대원의 이름은 "대원 {random_number}"로 설정됨
        """
        random_number = str(random.random()).split(".")[1]
        new_crew = cls(faction_id=faction_id, name=f"대원 {random_number}")
        new_crew.category = cls.correspond_category
        return new_crew

    def get_consumption_recipe(self) -> list[GeneralResource]:
        return [
            GeneralResource(ResourceCategory.FOOD, 1),
            GeneralResource(ResourceCategory.WATER, 1)
        ]

    def get_description(self) -> WorkerDescription:
        self._check_database()
        desc = WorkerDescription.from_data(self._database.fetch(WorkerDescription.get_table_name(), worker_id=self.id))
        if desc.worker_id != self.id: desc.worker_id = self.id
        return desc

    def get_experience(self, category: WorkCategory) -> WorkerExperience:
        self._check_database()
        we = WorkerExperience.from_data(
            self._database.fetch(WorkerExperience.get_table_name(), worker_id=self.id, experience_category=category.value)
        )
        if we.worker_id != self.id: we.worker_id = self.id
        return we

    def get_every_experience(self) -> list[WorkerExperience]:
        return [self.get_experience(category) for category in WorkCategory.to_list()]

    def set_labor_dice(self):

        self._labor_dice = Nonahedron()
        return self

    def get_labor_by_WorkCategory(self, category: WorkCategory):
        return self.labor + self.get_experience(category).level

    def set_labor(self):
        """
        노동력 설정
        """
        if self._labor_dice is None: self.set_labor_dice()
        self.labor = self._labor_dice.roll()
        return self

    def get_display_string(self) -> str:
        return self.name

    def is_available(self) -> bool:
        return self.availability.is_available()

class Livestock(Worker):
    abstract = False
    correspond_category = WorkerCategory.LIVESTOCK

    def __init__(self, **kwargs):
        Worker.__init__(self, **kwargs)
        Workable.__init__(self)

    def get_consumption_recipe(self) -> list[GeneralResource]:
        return [
            GeneralResource(ResourceCategory.FEED, 1),
            GeneralResource(ResourceCategory.WATER, 2)
        ]

    def get_display_string(self) -> str:
        if self.name:
            return self.name
        return f"가축 {self.id}"

    def set_labor_dice(self):
        """
        기본적으로 주사위 결과에 3을 더함 (최소 4)
        """
        self._labor_dice = Nonahedron(dice_mod=3)
        return self

    def set_labor(self):
        if self._labor_dice is None: self.set_labor_dice()
        self.labor = self._labor_dice.roll()
        return self

# 자원

class ProductionResource(ResourceAbst):
    
    def __init__(
        self, 
        category: ResourceCategory, 
        amount: int = 1, 
        dice_ratio: int = 1
    ):
        super().__init__(category, amount)
        self.dice_ratio = dice_ratio # 1 이상의 정수
    
    def __str__(self) -> str:
        return f"{self.category.name}; 주사위 값 {self.dice_ratio} 당 {self.amount}개 생산"
    
    def _return_general_resource(self, dice: int) -> GeneralResource:
        # dice_ratio 당 amount를 계산한다.
        # dice_ratio가 1이면 amount가 그대로 반환된다.
        # dice_ratio가 2이면 amount가 절반이 된다.
        
        return GeneralResource(self.category, self.amount * (dice // self.dice_ratio))
    
    def __mul__(self, other: int | Dice) -> GeneralResource:
        dice: int = 0
        if isinstance(other, int):
            dice = other
        elif isinstance(other, Dice):
            if other._last_roll is None: raise ValueError("주사위를 굴려주세요")
            dice = other._last_roll
        else:
            raise TypeError(f"int 또는 Dice 타입만 가능합니다. (현재 타입: {type(other)})")
        
        return self._return_general_resource(dice)

class ProductionRecipe:
    def __init__(
        self, *, 
        consume: list[GeneralResource] = [], 
        produce: list[ProductionResource] = []
    ):
        self.consume = consume
        self.produce = produce



    
    
# TODO schedule_manager의 building_produce 함수 기능을 여기로 끌어올 수 있을 텐데



# 건물


class SystemBuilding(Building, metaclass=ABCMeta):
    """
    시설 클래스들의 부모 클래스
    """
    building_category: BuildingCategory = BuildingCategory.UNSET
    labor_category: WorkCategory = WorkCategory.UNSET
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @abstractmethod
    def get_production_recipe(self) -> ProductionRecipe:
        return ProductionRecipe()

    @classmethod
    def from_building(cls, building: Building) -> "SystemBuilding":
        """
        Building 객체를 BuildingBase 하위 객체로 변환한다.
        """
        for sub_cls_type in cls.__subclasses__():
            if sub_cls_type.building_category.value == building.category.value:
                return sub_cls_type(**building.get_dict())
        raise ValueError(f"해당 카테고리({building.category})의 건물이 없습니다.")

    @classmethod
    def type_from_category(cls, category:BuildingCategory) -> Type["SystemBuilding"]:
        """
        BuildingBase를 상속받은 클래스들 중에서 category에 해당하는 클래스를 반환
        """
        for sub_cls_type in cls.__subclasses__():
            if sub_cls_type.building_category.value == category.value:
                return sub_cls_type
        raise ValueError(f"해당 카테고리({category})의 건물이 없습니다.")
    
    def produce_resource_by_crew(self, database: DatabaseManager, crew: Crew) -> Generator[Resource, None, None]:
        """
        해당 건물에서 일하는 노동 개체(대원, 가축)가 생산한 자원(Resource 객체)을 반환
        
        이 함수로 반환한 Resource 객체는 직접 database에 저장해야 한다. 단, database 등록은 되어 있다.
        """
        recipe = self.get_production_recipe()
        for produce_resource in recipe.produce:
            r_data = database.fetch(
                Resource.get_table_name(),
                faction_id = self.faction_id,
                category = produce_resource.category.value
            )
            resource = Resource.from_data(r_data, faction_id=self.faction_id, category=produce_resource.category)
            resource.set_database(database)
            
            produced_resource = produce_resource * crew.get_labor_by_WorkCategory(self.labor_category)
            resource.amount += produced_resource.amount
        
            yield resource
    
    def produce_resource_by_livestock(self, database: DatabaseManager, livestock: Workable) -> Generator[Resource, None, None]:
        
        recipe = self.get_production_recipe()
        for produce_resource in recipe.produce:
            r_data = database.fetch(
                Resource.get_table_name(),
                faction_id = self.faction_id,
                category = produce_resource.category.value
            )
            resource = Resource.from_data(r_data, faction_id=self.faction_id, category=produce_resource.category)
            resource.set_database(database)
            
            
            produced_resource = produce_resource * livestock.labor
            resource.amount += produced_resource.amount
        
            yield resource
    
    def get_construction_progress(self) -> int:
        return self.required_dice_cost - self.remaining_dice_cost
    
    # def construct(self, deployed_crews: list[Crew]):
    #     if self.is_built(): return
        
    #     for crew in deployed_crews:
    #         construction_exp = crew.get_experience(LaborCategory.CONSTRUCTION)
    #         construction_dice = construction_exp.get_labor_dice()
    #         construction_dice.roll()
            
    #         self.apply_production(construction_dice.last_roll)

class BasicBuilding(metaclass=ABCMeta):
    """
    기초 건물 클래스들의 부모 클래스
    """
    pass


class AdvancedBuilding(metaclass=ABCMeta):
    """
    고급 건물 클래스들의 부모 클래스
    """
    pass


class FreshWaterSource(SystemBuilding, BasicBuilding):
    building_category = BuildingCategory.FRESH_WATER_SOURCE
    labor_category = WorkCategory.GATHERING
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WATER, dice_ratio=2)]
        )


class HuntingGround(SystemBuilding, BasicBuilding):
    building_category = BuildingCategory.HUNTING_GROUND
    labor_category = WorkCategory.HUNTING
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        """
        사냥
        """
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.FOOD, amount=3, dice_ratio=7)]
        )


class GatheringPost(SystemBuilding, BasicBuilding):
    building_category = BuildingCategory.GATHERING_POST
    labor_category = WorkCategory.GATHERING
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        """
        채집
        """
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.FOOD, dice_ratio=3)]
        )


class Pastureland(SystemBuilding, BasicBuilding):
    building_category = BuildingCategory.PASTURELAND
    labor_category = WorkCategory.HUNTING
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.LIVESTOCK, dice_ratio=9)]
        )


class Farmland(SystemBuilding, AdvancedBuilding):
    building_category = BuildingCategory.FARMLAND
    labor_category = WorkCategory.AGRICULTURE
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            consume=[GeneralResource(ResourceCategory.WATER)],
            produce=[ProductionResource(ResourceCategory.FOOD, dice_ratio=2)]
        )


class WoodGatheringPost(SystemBuilding, AdvancedBuilding):
    building_category = BuildingCategory.WOOD_GATHERING_POST
    labor_category = WorkCategory.GATHERING
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WOOD, dice_ratio=3)]
        )


class EarthGatheringPost(SystemBuilding, AdvancedBuilding):
    building_category = BuildingCategory.EARTH_GATHERING_POST
    labor_category = WorkCategory.GATHERING
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[
                ProductionResource(ResourceCategory.SOIL, dice_ratio=3),
                ProductionResource(ResourceCategory.STONE, dice_ratio=3)
            ]
        )


class BuildingMaterialFactory(SystemBuilding, AdvancedBuilding):
    building_category = BuildingCategory.BUILDING_MATERIAL_FACTORY
    labor_category = WorkCategory.MANUFACTURING
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            consume=[
                GeneralResource(ResourceCategory.SOIL), 
                GeneralResource(ResourceCategory.STONE), 
                GeneralResource(ResourceCategory.WOOD)
            ],
            produce=[ProductionResource(ResourceCategory.BUILDING_MATERIAL, dice_ratio=2)]
        )


class RecruitingCamp(SystemBuilding, AdvancedBuilding):
    building_category = BuildingCategory.RECRUITING_CAMP
    labor_category = WorkCategory.UNSET
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        """
        이 건물은 아무것도 생산하지 않는다.
        """
        return ProductionRecipe()


class AutomatedGatheringFacility(SystemBuilding, AdvancedBuilding):
    building_category = BuildingCategory.AUTOMATED_GATHERING_FACILITY
    labor_category = WorkCategory.UNSET
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        raise NotImplementedError("자동 채집 시설은 아직 구현되지 않았습니다.")





# ()
# class Reservoir(Storages):
#     category: int = 3
#     name: str = "저수지"
#     required_dice_cost: int = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.WATER, 20),
#         ]
#     )

# ()
# class Granary(Storages):
#     category: int = 4
#     name: str = "곡창"
#     required_dice_cost: int = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.FOOD, 20),
#             GeneralResource(ResourceCategory.FEED, 20)
#         ]
#     )

# ()
# class BuildingMaterialStorage(Storages):
#     category: int = 5
#     name: str = "건자재 창고"
#     required_dice_cost: int = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource("building_material", 20),
#         ]
#     )