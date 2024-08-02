import _pre
_pre.add_parent_dir_to_sys_path()

from py_base import ari_enum

ts = ari_enum.TerritorySafety.get_randomly()

print(
    ts.name, ts.value, ts.express()
)