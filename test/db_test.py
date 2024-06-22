import _pre
_pre.add_parent_dir_to_sys_path()

from py_base.dbmanager import DatabaseManager
from py_system.systemobj import SystemBuilding
from py_system.tableobj import form_database_from_tableobjects

db = DatabaseManager("main_test")
form_database_from_tableobjects(db)