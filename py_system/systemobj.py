"""
table object와 연계되는 데이터 클래스, 하지만 db에 직접 저장되지 않는다.
"""
from dataclasses import dataclass, field
from py_base.ari_enum import ResourceCategory, BuildingCategory
from py_system import tableobj
from py_system.abstract import ResourceBase, BasicBuilding, AdvancedBuilding
from py_system.arislena_dice import Dice

class Client:
    
    def __init__(self, user:tableobj.User = None, faction:tableobj.Faction = None):
        """
        데이터베이스에 저장된 유저 정보를 받아서 클라이언트를 생성한다.
        """
        self.user = user
        self.faction = faction
        self.command_counter = faction.get_command_counter() if faction else None

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
class FreshWaterSource(BasicBuilding):
    category = BuildingCategory.FRESH_WATER_SOURCE
    dice_cost: int = 0
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WATER, dice_ratio=3)]
        )

@dataclass
class HuntingGround(BasicBuilding):
    category = BuildingCategory.HUNTING_GROUND
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
class Pastureland(BasicBuilding):
    category = BuildingCategory.PASTURELAND
    dice_cost: int = 0
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.LIVESTOCK, dice_ratio=9)]
        )

@dataclass
class Farmland(AdvancedBuilding):
    category = BuildingCategory.FARMLAND
    dice_cost: int = 30
    
    def produce(self):
        return ProductionRecipe(
            consume=[GeneralResource(ResourceCategory.WATER)],
            produce=[ProductionResource(ResourceCategory.FOOD, dice_ratio=2)]
        )

@dataclass
class WoodGatheringPost(AdvancedBuilding):
    category = BuildingCategory.WOOD_GATHERING_POST
    dice_cost: int = 30
    
    def produce(self):
        return ProductionRecipe(
            produce=[ProductionResource(ResourceCategory.WOOD, dice_ratio=3)]
        )

@dataclass
class EarthGatheringPost(AdvancedBuilding):
    category = BuildingCategory.EARTH_GATHERING_POST
    dice_cost: int = 30
    
    def produce(self):
        return ProductionRecipe(
            produce=[
                ProductionResource(ResourceCategory.SOIL, dice_ratio=3),
                ProductionResource(ResourceCategory.STONE, dice_ratio=3)
            ]
        )

@dataclass
class BuildingMaterialFactory(AdvancedBuilding):
    category = BuildingCategory.BUILDING_MATERIAL_FACTORY
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
class RecruitingCamp(AdvancedBuilding):
    category = BuildingCategory.RECRUITING_CAMP
    dice_cost: int = 30
    
    def produce(self):
        """
        이 건물은 아무것도 생산하지 않는다.
        """
        return 

@dataclass
class AutomatedGatheringFacility(AdvancedBuilding):
    category = BuildingCategory.AUTOMATED_GATHERING_FACILITY
    dice_cost: int = 30
    
    def produce(self):
        raise NotImplementedError("자동 채집 시설은 아직 구현되지 않았습니다.")

# @dataclass()
# class Reservoir(Storages):
#     category: int = 3
#     name: str = "저수지"
#     dice_cost: int = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource(ResourceCategory.WATER, 20),
#         ]
#     )

# @dataclass()
# class Granary(Storages):
#     category: int = 4
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
#     category: int = 5
#     name: str = "건자재 창고"
#     dice_cost: int = 30
#     storages: list[GeneralResource] = field(
#         default_factory=lambda: [
#             GeneralResource("building_material", 20),
#         ]
#     )