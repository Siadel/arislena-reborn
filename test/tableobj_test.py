import _pre
_pre.add_parent_dir_to_sys_path()

from py_base.dbmanager import DatabaseManager

from py_system import tableobj
from py_system import worker, facility

# for subcls in tableobj.TableObject.__subclasses__():
#     print(subcls.__name__, subcls.table_name, subcls.__name__ in subcls.table_name)

# db = DatabaseManager("test")

# w = tableobj.Worker()
# print(w.get_dict())
# print(w.get_insert_information())
# print(w.get_update_query())

for subcls in tableobj.TableObject.__subclasses__():
    if not subcls.table_name: continue
    print(subcls.__name__)
    print(subcls().get_insert_information())
    print(subcls().get_update_query())
    print(subcls.get_create_table_query())
    print("\n")