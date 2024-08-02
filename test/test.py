import _pre
_pre.add_parent_dir_to_sys_path()

import random
from math import sqrt

from py_base import utility, ari_enum
# from py_system.tableobj import Facility
from py_system.facility import category_to_facility

# s = {}
# for _ in range(100):
    
#     v = random.choices([0, 1, 2], [0.2, 0.7, 0.1])[0]
#     s[v] = s.get(v, 0) + 1

# print(s)

# print(
#     issubclass(FreshWaterSource, Facility)
# )

print(
    category_to_facility(ari_enum.FacilityCategory.CLINIC)
)