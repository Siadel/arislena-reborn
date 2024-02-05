from dataclasses import dataclass, field

from py_system.abstract import Buildings, Storages, Resource

@dataclass()
class DefaultResource(Resource):
    name: str
    amount: int

@dataclass()
class ConsumptionResource(Resource):
    name: str # water, food, feed, wood, soil, stone, building_material
    amount: int

@dataclass()
class ProductionResource(Resource):
    name: str
    amount: float # 주사위 1당 생산량

@dataclass()
class Farm(Buildings):
    discriminator: int = 0
    name: str = "농경지"
    dice_cost: int = 30
    consumptions: list[ConsumptionResource] = field(
        default_factory=lambda: [
            ConsumptionResource("food", 1),
            ConsumptionResource("water", 1)
        ]
    )
    productions: list[ProductionResource] = field(
        default_factory=lambda: [
            ProductionResource("food", 0.5),
            ProductionResource("feed", 0.5)
        ]
    )

@dataclass()
class WoodGatheringPost(Buildings):
    discriminator: int = 1
    name: str = "목재 채취장"
    dice_cost: int = 30
    consumptions: list[ConsumptionResource] = field(
        default_factory=lambda: [
            ConsumptionResource("food", 1)
        ]
    )
    productions: list[ProductionResource] = field(
        default_factory=lambda: [
            ProductionResource("wood", 0.5),
            ProductionResource("stone", 0.5)
        ]
    )

@dataclass()
class EarthGatheringPost(Buildings):
    discriminator: int = 2
    name: str = "토석 채취장"
    dice_cost: int = 30
    consumptions: list[ConsumptionResource] = field(
        default_factory=lambda: [
            ConsumptionResource("food", 1),
            ConsumptionResource("soil", 1),
            ConsumptionResource("stone", 1),
            ConsumptionResource("wood", 1)
        ]
    )
    productions: list[ProductionResource] = field(
        default_factory=lambda: [
            ProductionResource("building_material", 0.5)
        ]
    )

@dataclass()
class Reservoir(Storages):
    discriminator: int = 3
    name: str = "저수지"
    dice_cost: int = 30
    storages: list[DefaultResource] = field(
        default_factory=lambda: [
            DefaultResource("water", 20),
        ]
    )

@dataclass()
class Granary(Storages):
    discriminator: int = 4
    name: str = "곡창"
    dice_cost: int = 30
    storages: list[DefaultResource] = field(
        default_factory=lambda: [
            DefaultResource("food", 20),
            DefaultResource("feed", 20)
        ]
    )

@dataclass()
class BuildingMaterialStorage(Storages):
    discriminator: int = 5
    name: str = "건자재 창고"
    dice_cost: int = 30
    storages: list[DefaultResource] = field(
        default_factory=lambda: [
            DefaultResource("building_material", 20),
        ]
    )