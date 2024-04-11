"""
table object와 연계되는 데이터 클래스, 하지만 db에 직접 저장되지 않는다.
"""
from abc import ABCMeta, abstractmethod
from typing import Type

from py_base.ari_enum import ResourceCategory, BuildingCategory
from py_base.arislena_dice import Dice
from py_system.abstract import ResourceAbst
from py_system.tableobj import Building

# 자원

class GeneralResource(ResourceAbst):
    
    def __init__(
        self, 
        category: ResourceCategory, 
        amount: int = 1
    ):
        super().__init__(category, amount)


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
            if other.last_roll is None: raise ValueError("주사위를 굴려주세요")
            dice = other.last_roll
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
    corr_category: BuildingCategory = BuildingCategory.UNSET
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @abstractmethod
    def get_production_recipe(self) -> ProductionRecipe:
        return ProductionRecipe()

    @classmethod
    def get_sys_building_from_building(cls, building: Building) -> "SystemBuilding":
        """
        Building 객체를 BuildingBase 하위 객체로 변환한다.
        """
        for sub_cls_type in cls.__subclasses__():
            if sub_cls_type.corr_category.value == building.category.value:
                return sub_cls_type(**building.get_dict())
        raise ValueError(f"해당 카테고리({building.category})의 건물이 없습니다.")

    @classmethod
    def get_sys_building_type_from_category(cls, category:BuildingCategory) -> Type["SystemBuilding"]:
        """
        BuildingBase를 상속받은 클래스들 중에서 category에 해당하는 클래스를 반환
        """
        for sub_cls_type in cls.__subclasses__():
            if sub_cls_type.corr_category.value == category.value:
                return sub_cls_type
        raise ValueError(f"해당 카테고리({category})의 건물이 없습니다.")

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
    corr_category: BuildingCategory = BuildingCategory.FRESH_WATER_SOURCE
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WATER, dice_ratio=3)]
        )


class HuntingGround(SystemBuilding, BasicBuilding):
    corr_category: BuildingCategory = BuildingCategory.HUNTING_GROUND
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
    corr_category: BuildingCategory = BuildingCategory.GATHERING_POST
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
    corr_category: BuildingCategory = BuildingCategory.PASTURELAND
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.LIVESTOCK, dice_ratio=9)]
        )


class Farmland(SystemBuilding, AdvancedBuilding):
    corr_category: BuildingCategory = BuildingCategory.FARMLAND
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            consume=[GeneralResource(ResourceCategory.WATER)],
            produce=[ProductionResource(ResourceCategory.FOOD, dice_ratio=2)]
        )


class WoodGatheringPost(SystemBuilding, AdvancedBuilding):
    corr_category: BuildingCategory = BuildingCategory.WOOD_GATHERING_POST
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WOOD, dice_ratio=3)]
        )


class EarthGatheringPost(SystemBuilding, AdvancedBuilding):
    corr_category: BuildingCategory = BuildingCategory.EARTH_GATHERING_POST
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
    corr_category: BuildingCategory = BuildingCategory.BUILDING_MATERIAL_FACTORY
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
    corr_category: BuildingCategory = BuildingCategory.RECRUITING_CAMP
    required_dice_cost: int = 30
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def get_production_recipe(self):
        """
        이 건물은 아무것도 생산하지 않는다.
        """
        return ProductionRecipe()


class AutomatedGatheringFacility(SystemBuilding, AdvancedBuilding):
    corr_category: BuildingCategory = BuildingCategory.AUTOMATED_GATHERING_FACILITY
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