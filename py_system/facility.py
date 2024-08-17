from abc import ABCMeta

from py_base import ari_enum, utility
from py_system.abstract import ProductionResource, ProductionRecipe, GeneralResource
from py_system.tableobj import Facility

def category_to_facility(category: ari_enum.FacilityCategory) -> type[Facility]:
    """
    시설 카테고리를 입력받아 해당하는 시설 객체를 반환합니다.
    """
    return utility.select_from_subclasses(
        Facility,
        facility_category=category
    )

def facility_to_concrete_facility(facility: Facility) -> Facility:
    """
    Facility 객체를 FacilityBase 하위 객체로 변환합니다.
    """
    return category_to_facility(facility.category)(**facility.get_dict())

class NatureFacility(metaclass=ABCMeta):
    pass

class AdvancedFacility(metaclass=ABCMeta):
    """
    고급 시설 클래스들의 부모 클래스
    """
    pass

class FreshWaterSource(Facility, NatureFacility):
    facility_category = ari_enum.FacilityCategory.FRESH_WATER_SOURCE
    work_category = ari_enum.WorkCategory.GATHERING
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ari_enum.ResourceCategory.WATER, dice_ratio=5)]
        )


class HuntingGround(Facility, NatureFacility):
    facility_category = ari_enum.FacilityCategory.HUNTING_GROUND
    work_category = ari_enum.WorkCategory.HUNTING
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        """
        사냥
        """
        return ProductionRecipe(
            produce=[ProductionResource(ari_enum.ResourceCategory.FOOD, amount=3, dice_ratio=12)]
        )


class GatheringPost(Facility, NatureFacility):
    facility_category = ari_enum.FacilityCategory.GATHERING_POST
    work_category = ari_enum.WorkCategory.GATHERING
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        """
        채집
        """
        return ProductionRecipe(
            produce=[ProductionResource(ari_enum.ResourceCategory.FOOD, dice_ratio=5)]
        )


class Pastureland(Facility, NatureFacility):
    facility_category = ari_enum.FacilityCategory.PASTURELAND
    work_category = ari_enum.WorkCategory.HUNTING
    required_dice_cost: int = 0
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ari_enum.ResourceCategory.LIVESTOCK, dice_ratio=15)]
        )


class Farmland(Facility, AdvancedFacility):
    facility_category = ari_enum.FacilityCategory.FARMLAND
    work_category = ari_enum.WorkCategory.AGRICULTURE
    required_dice_cost: int = 70
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            consume=[GeneralResource(ari_enum.ResourceCategory.WATER)],
            produce=[ProductionResource(ari_enum.ResourceCategory.FOOD, dice_ratio=3)]
        )


class WoodGatheringPost(Facility, AdvancedFacility):
    facility_category = ari_enum.FacilityCategory.WOOD_GATHERING_POST
    work_category = ari_enum.WorkCategory.GATHERING
    required_dice_cost: int = 70
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[ProductionResource(ari_enum.ResourceCategory.WOOD, dice_ratio=5)]
        )


class EarthGatheringPost(Facility, AdvancedFacility):
    facility_category = ari_enum.FacilityCategory.EARTH_GATHERING_POST
    work_category = ari_enum.WorkCategory.GATHERING
    required_dice_cost: int = 70
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            produce=[
                ProductionResource(ari_enum.ResourceCategory.SOIL, dice_ratio=5),
                ProductionResource(ari_enum.ResourceCategory.STONE, dice_ratio=5)
            ]
        )


class FacilityMaterialFactory(Facility, AdvancedFacility):
    facility_category = ari_enum.FacilityCategory.BUILDING_MATERIAL_FACTORY
    work_category = ari_enum.WorkCategory.MANUFACTURING
    required_dice_cost: int = 70
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        return ProductionRecipe(
            consume=[
                GeneralResource(ari_enum.ResourceCategory.SOIL), 
                GeneralResource(ari_enum.ResourceCategory.STONE), 
                GeneralResource(ari_enum.ResourceCategory.WOOD)
            ],
            produce=[ProductionResource(ari_enum.ResourceCategory.BUILDING_MATERIAL, dice_ratio=5)]
        )


class RecruitingCamp(Facility, AdvancedFacility):
    facility_category = ari_enum.FacilityCategory.RECRUITING_CAMP
    work_category = ari_enum.WorkCategory.UNSET
    required_dice_cost: int = 70
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        """
        이 시설은 아무것도 생산하지 않는다.
        """
        return ProductionRecipe()


class SupplyBase(Facility, AdvancedFacility):
    facility_category = ari_enum.FacilityCategory.SUPPLY_BASE
    work_category = ari_enum.WorkCategory.UNSET
    required_dice_cost: int = 140
    
    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)
    
    def get_production_recipe(self):
        raise NotImplementedError(f"{ari_enum.FacilityCategory.SUPPLY_BASE.local_name}은 아직 구현되지 않았습니다.")


class Clinic(Facility, AdvancedFacility):
    facility_category = ari_enum.FacilityCategory.CLINIC
    work_category = ari_enum.WorkCategory.TREAT
    required_dice_cost = 70

    def __init__(self, **kwargs):
        Facility.__init__(self, **kwargs)

    def get_production_recipe(self):
        raise NotImplementedError("진료소는 아직 구현되지 않았습니다.")
