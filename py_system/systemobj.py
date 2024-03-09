"""
table object와 연계되는 데이터 클래스, 하지만 db에 직접 저장되지 않는다.
"""

from dataclasses import dataclass, field
from py_base.ari_enum import ResourceCategory, BuildingCategory
from py_base.datatype import ExtInt
from py_base.abstract import Buildings, ResourceBase
from py_system.arislena_dice import Dice

@dataclass
class GeneralResource(ResourceBase):
    category: ResourceCategory
    amount: int = 1

@dataclass
class ProductionResource:
    category: ResourceCategory
    amount: int = 1
    dice_ratio: int = 1
    
    def __str__(self) -> str:
        return f"{self.category.name}; 주사위 값 {self.dice_ratio} 당 {self.amount}개 생산"
    
    def _return_general_resource(self, dice: int) -> GeneralResource:
        # dice_ratio 당 amount를 계산한다.
        # dice_ratio가 1이면 amount가 그대로 반환된다.
        # dice_ratio가 2이면 amount가 절반이 된다.
        
        return GeneralResource(self.category, self.amount * (dice // self.dice_ratio))
    
    def __mul__(self, other: int | Dice) -> GeneralResource:
        dice: int = other if isinstance(other, int) else 0
        if isinstance(other, Dice):
            if other.last_roll is None: raise ValueError("주사위를 굴려주세요")
            dice = other.last_roll
        
        return self._return_general_resource(dice)

class ProductionRecipe:
    def __init__(self, *, consume: list[GeneralResource] = [], produce: list[ProductionResource] = []):
        self.consume = consume
        self.produce = produce

# 건물

@dataclass
class FreshWaterSource(Buildings):
    discriminator = BuildingCategory.FRESH_WATER_SOURCE
    dice_cost: int = 0
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WATER, dice_ratio=3)]
        )

@dataclass
class HuntingGround(Buildings):
    discriminator = BuildingCategory.HUNTING_GROUND
    dice_cost: int = 0
    
    def produce(self):
        """
        사냥
        """
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.FOOD, amount=3, dice_ratio=7)]
        )
    
    def produce_alias(self):
        """
        채집
        """
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WOOD, dice_ratio=3)]
        )

@dataclass
class Pastureland(Buildings):
    discriminator = BuildingCategory.PASTURELAND
    dice_cost: int = 0
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.LIVESTOCK, dice_ratio=9)]
        )

@dataclass
class Farmland(Buildings):
    discriminator = BuildingCategory.FARMLAND
    dice_cost: int = 30
    
    def produce(self):
        return ProductionRecipe(
            consume=[GeneralResource(ResourceCategory.WATER)],
            produce=[ProductionResource(ResourceCategory.FOOD, dice_ratio=2)]
        )

@dataclass
class WoodGatheringPost(Buildings):
    discriminator = BuildingCategory.WOOD_GATHERING_POST
    dice_cost: int = 30
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WOOD, dice_ratio=3)]
        )

@dataclass
class EarthGatheringPost(Buildings):
    discriminator = BuildingCategory.EARTH_GATHERING_POST
    dice_cost: int = 30
    
    def produce(self):
        return ProductionRecipe(
            produce=[
                ProductionResource(ResourceCategory.SOIL, dice_ratio=3),
                ProductionResource(ResourceCategory.STONE, dice_ratio=3)
            ]
        )

@dataclass
class BuildingMaterialFactory(Buildings):
    discriminator = BuildingCategory.BUILDING_MATERIAL_FACTORY
    dice_cost: int = 30
    
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
class RecruitingCamp(Buildings):
    discriminator = BuildingCategory.RECRUITING_CAMP
    dice_cost: int = 30
    
    def produce(self):
        """
        이 건물은 아무것도 생산하지 않는다.
        """
        return 

@dataclass
class AutomatedGatheringFacility(Buildings):
    discriminator = BuildingCategory.AUTOMATED_GATHERING_FACILITY
    dice_cost: int = 30
    
    def produce(self):
        raise NotImplementedError("자동 채집 시설은 아직 구현되지 않았습니다.")

# @dataclass()
# class Reservoir(Storages):
#     discriminator: int = 3
#     name: str = "저수지"
#     dice_cost: int = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.WATER, 20),
#         ]
#     )

# @dataclass()
# class Granary(Storages):
#     discriminator: int = 4
#     name: str = "곡창"
#     dice_cost: int = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.FOOD, 20),
#             GeneralResource(ResourceCategory.FEED, 20)
#         ]
#     )

# @dataclass()
# class BuildingMaterialStorage(Storages):
#     discriminator: int = 5
#     name: str = "건자재 창고"
#     dice_cost: int = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource("building_material", 20),
#         ]
#     )