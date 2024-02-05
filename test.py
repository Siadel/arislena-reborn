from py_system.global_ import main_db
from py_system.tableobj import form_database_from_tableobjects, User, Faction

faction = Faction()
faction.name = "생존자들"
faction.level = 1
faction.database = main_db
faction.push()

# faction = main_db.fetch("faction", "ID = 1")
# faction.name = "생존자들"
# faction.level = 1
# main_db.update_as(faction)

# print(
#     main_db.fetch("faction", "id = (SELECT MIN(id) FROM faction)")
# )

# main_db.set_hierarchy(
#     main_db.fetch("faction", "ID = 2"),
#     main_db.fetch("faction", "ID = 1")
# )

form_database_from_tableobjects(main_db)
dummy_user = User(
    0,
    1234567890,
    "Dummy",
    "1900-01-01"
)
dummy_user.database = main_db
dummy_user.push()
fetched_user = User(**main_db.fetch("user", discord_id=1234567890))
print(fetched_user)

# from py_system.buildings import Farm, WoodGatheringPost
# from dataclasses import dataclass, field, asdict
# 테스트 코드 작성

# farm = Farm()
# wgp = WoodGatheringPost()
# print(asdict(farm), asdict(wgp))

# class A:
    
#     def __init__(self):
#         self.a = 1
#         self.b = 2
#         self.c = 3

# print(A.__annotations__)

# from py_system.tableobj import Faction
# faction = Faction()
# print(faction.get_create_table_string())