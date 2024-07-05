import _pre
_pre.add_parent_dir_to_sys_path()

from pprint import pprint

from py_base.yamlwork import load_yaml
from py_base.yamlobj import TableObjTranslator

pprint(
    load_yaml("scenario.yaml"),
    sort_dicts=False
)