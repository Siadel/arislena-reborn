from py_base.ari_enum import Troop
from py_system.tableobj import Faction
print(type(Troop.IDLE), Troop(1), Troop(1).name, type(Troop(1)))
# f = Faction()
# print(f.__dict__)
# for annotation in f.__annotations__:
#     print(annotation, f.__annotations__[annotation], type(f.__annotations__[annotation]))