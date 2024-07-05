import _pre
_pre.add_parent_dir_to_sys_path()

from py_base import ari_enum

print(
    ari_enum.BiologicalSex.get_random()
)