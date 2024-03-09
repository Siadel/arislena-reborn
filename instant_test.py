from pprint import pprint

from py_base.ari_enum import ResourceCategory, ArislenaEnum
from py_system._global import main_db
from py_system.tableobj import Resource, Faction, form_database_from_tableobjects
from py_system.systemobj import ResourceBase, ProductionResource, GeneralResource
from py_system.arislena_dice import Nonahedron




# dice = Nonahedron()
# dice.roll()

# print(f"주사위 굴린 결과: {dice.last_roll}")

# pr = ProductionResource(ResourceCategory.FOOD, 3, dice_ratio=7)

# print(f"ProductionResource: {pr.__repr__()}")

# prdice = pr * dice

# print(f"ProductionResource * dice: {(prdice).__repr__()} {prdice} {int(prdice)}")