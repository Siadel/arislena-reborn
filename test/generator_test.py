import _pre
_pre.add_parent_dir_to_sys_path()

from typing import Generator

from py_base.ari_enum import BuildingCategory
from py_system.tableobj import Building
from py_system.systemobj import SystemBuilding

fws = SystemBuilding.from_building(
    Building(0, 0, 0, BuildingCategory.FRESH_WATER_SOURCE, "테스트", 0, 0)
)
fws.produce_resource_by_crew()