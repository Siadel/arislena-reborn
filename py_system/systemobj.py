"""
table object와 연계되는 데이터 클래스, 하지만 db에 직접 저장되지 않는다.
"""
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod
from typing import ClassVar

from py_base.ari_enum import ResourceCategory, BuildingCategory
from py_base.arislena_dice import Dice
from py_system.abstract import ResourceBase
from py_system.tableobj import Building

# 자원

@dataclass
class GeneralResource(ResourceBase):
    category: ResourceCategory
    amount: int = 1

@dataclass
class ProductionResource:
    category: ResourceCategory
    amount: int = 1
    dice_ratio: int = 1 # 1 이상의 정수
    
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

# 건물
 
@dataclass
class BuildingBase(Building, metaclass=ABCMeta):
    """
    시설 클래스들의 부모 클래스
    """
    category: ClassVar[BuildingCategory] = BuildingCategory.UNSET
    required_dice_cost: ClassVar[int] = 0
    
    @abstractmethod
    def produce(self) -> ProductionRecipe:
        raise ProductionRecipe()
    
    @classmethod
    def from_building(cls, building:Building) -> "BuildingBase":
        t = cls.get_building_type_by_category(building.category)
        return t(**building.get_dict())
    
    @classmethod
    def get_building_type_by_category(cls, category:BuildingCategory):
        """
        BuildingBase를 상속받은 클래스들 중에서 category에 해당하는 클래스를 반환
        """
        for sub_cls_type in cls.__subclasses__():
            if sub_cls_type.category == category:
                return sub_cls_type
        raise ValueError(f"해당 카테고리({category})의 건물이 없습니다.")

@dataclass
class BasicBuilding(BuildingBase, metaclass=ABCMeta):
    """
    기초 건물 클래스들의 부모 클래스
    """

    def produce(self) -> ProductionRecipe:
        super().produce()

@dataclass
class AdvancedBuilding(BuildingBase, metaclass=ABCMeta):
    """
    고급 건물 클래스들의 부모 클래스
    """

    def produce(self) -> ProductionRecipe:
        super().produce()

@dataclass
class FreshWaterSource(BasicBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.FRESH_WATER_SOURCE
    required_dice_cost: ClassVar[int] = 0
    
    @classmethod
    def from_building(cls, building:Building) -> "FreshWaterSource":
        return cls(**building.get_dict())
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WATER, dice_ratio=3)]
        )

@dataclass
class HuntingGround(BasicBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.HUNTING_GROUND
    required_dice_cost: ClassVar[int] = 0
    
    def produce(self):
        """
        사냥
        """
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.FOOD, amount=3, dice_ratio=7)]
        )

@dataclass
class GatheringPost(BasicBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.GATHERING_POST
    required_dice_cost: ClassVar[int] = 0
    
    def produce(self):
        """
        채집
        """
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.FOOD, dice_ratio=3)]
        )

@dataclass
class Pastureland(BasicBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.PASTURELAND
    required_dice_cost: ClassVar[int] = 0
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.LIVESTOCK, dice_ratio=9)]
        )

@dataclass
class Farmland(AdvancedBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.FARMLAND
    required_dice_cost: ClassVar[int] = 30
    
    def produce(self):
        return ProductionRecipe(
            consume=[GeneralResource(ResourceCategory.WATER)],
            produce=[ProductionResource(ResourceCategory.FOOD, dice_ratio=2)]
        )

@dataclass
class WoodGatheringPost(AdvancedBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.WOOD_GATHERING_POST
    required_dice_cost: ClassVar[int] = 30
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WOOD, dice_ratio=3)]
        )

@dataclass
class EarthGatheringPost(AdvancedBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.EARTH_GATHERING_POST
    required_dice_cost: ClassVar[int] = 30
    
    def produce(self):
        return ProductionRecipe(
            produce=[
                ProductionResource(ResourceCategory.SOIL, dice_ratio=3),
                ProductionResource(ResourceCategory.STONE, dice_ratio=3)
            ]
        )

@dataclass
class BuildingMaterialFactory(AdvancedBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.BUILDING_MATERIAL_FACTORY
    required_dice_cost: ClassVar[int] = 30
    
    def produce(self):
        return ProductionRecipe(
            consume=[
                GeneralResource(ResourceCategory.SOIL), 
                GeneralResource(ResourceCategory.STONE), 
                GeneralResource(ResourceCategory.WOOD)
            ],
            produce=[ProductionResource(ResourceCategory.BUILDING_MATERIAL, dice_ratio=2)]
        )

@dataclass
class RecruitingCamp(AdvancedBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.RECRUITING_CAMP
    required_dice_cost: ClassVar[int] = 30
    
    def produce(self):
        """
        이 건물은 아무것도 생산하지 않는다.
        """
        return ProductionRecipe()

@dataclass
class AutomatedGatheringFacility(AdvancedBuilding):
    category: ClassVar[BuildingCategory] = BuildingCategory.AUTOMATED_GATHERING_FACILITY
    required_dice_cost: ClassVar[int] = 30
    
    def produce(self):
        raise NotImplementedError("자동 채집 시설은 아직 구현되지 않았습니다.")


# @dataclass()
# class Reservoir(Storages):
#     category: int = 3
#     name: str = "저수지"
#     required_dice_cost: ClassVar[int] = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.WATER, 20),
#         ]
#     )

# @dataclass()
# class Granary(Storages):
#     category: int = 4
#     name: str = "곡창"
#     required_dice_cost: ClassVar[int] = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.FOOD, 20),
#             GeneralResource(ResourceCategory.FEED, 20)
#         ]
#     )

# @dataclass()
# class BuildingMaterialStorage(Storages):
#     category: int = 5
#     name: str = "건자재 창고"
#     required_dice_cost: ClassVar[int] = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource("building_material", 20),
#         ]
#     )