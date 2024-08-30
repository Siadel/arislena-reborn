import _pre
_pre.add_parent_dir_to_sys_path()

import random
from math import sqrt

from py_base import utility, ari_enum
# from py_system.tableobj import Facility
from py_system.resource import Spades
from py_system import tableobj
from py_system.facility import StatPerLevelConfig

# spades = Spades(2)
# spades += 2

# print(
#     spades
# )

# splc1 = StatPerLevelConfig(12, 2, -1, -3)
# splc2 = StatPerLevelConfig(1, 4, 1, 2)
splc3 = StatPerLevelConfig(50, 1, 15)
for level in range(15):
    print(
        f"level {level} : {splc3.calculate(level)}"
    )

# resource = tableobj.Resource(
#     category=ari_enum.ResourceCategory.SPADES,
#     amount=3
# )

# general = GeneralResource(
#     category=ari_enum.ResourceCategory.SPADES,
#     amount=5
# )

# resource += general

# print(
#     type(resource), resource.get_dict()
# )