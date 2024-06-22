import _pre
_pre.add_parent_dir_to_sys_path()

from py_base.yamlwork import load_yaml
from py_base.yamlobj import TableObjTranslate

print(TableObjTranslate().data)