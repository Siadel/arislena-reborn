import _pre
_pre.add_parent_dir_to_sys_path()

from py_base.dbmanager import DatabaseManager
from py_system.systemobj import SystemFacility
from py_system.tableobj import form_database_from_tableobjects

db = DatabaseManager("1153637128383770644")

print(
    db.fetch_many("WorkerExperience", "category > 0", worker_id=1)
)