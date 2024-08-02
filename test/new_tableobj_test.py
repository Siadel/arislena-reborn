import _pre
_pre.add_parent_dir_to_sys_path()

from py_base.dbmanager import DatabaseManager

from py_system import tableobj
from py_system import worker, facility

# for subcls in tableobj.TableObject.__subclasses__():
#     print(subcls.__name__, subcls.table_name, subcls.__name__ in subcls.table_name)

db = DatabaseManager("test")
tableobj.form_database_from_tableobjects(db)

# print(
#     facility.Farmland.from_database(db, id=1).get_dict()
# )