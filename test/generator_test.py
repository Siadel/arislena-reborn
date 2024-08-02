import _pre
_pre.add_parent_dir_to_sys_path()

from typing import Generator

from py_base.ari_enum import FacilityCategory
from py_system.tableobj import Facility
from py_system.systemobj import SystemFacility

fws = SystemFacility.from_facility(
    Facility(0, 0, 0, FacilityCategory.FRESH_WATER_SOURCE, "테스트", 0, 0)
)
fws.produce_resource_by_worker()