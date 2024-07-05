import _pre
_pre.add_parent_dir_to_sys_path()

from py_system.abstract import Column, TableObject
from py_system.tableobj import Resource, Worker
from py_base.ari_enum import ResourceCategory, WorkerCategory

from py_system.systemobj import SystemWorker, Crew
from py_base.yamlobj import TableObjTranslator

w = Worker()
c = Crew.new(2)

# tt = TableObjTranslator()

