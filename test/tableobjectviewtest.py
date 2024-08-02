import _pre
_pre.add_parent_dir_to_sys_path()

from py_base.dbmanager import DatabaseManager
from py_system.tableobj import User

db = DatabaseManager("1153637128383770644")

user_fetch_list = db.fetch_all(User.table_name)
user_list = [User.from_data(data) for data in user_fetch_list]

print(
    user_fetch_list
)

print(
    user_list
)