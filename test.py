# from py_base.ari_enum import TerritorySafety, get_enum
# from enum import Enum
from py_system.tableobj import Territory
from py_discord.embeds import table_info_text_list

from py_system.global_ import main_db



t = Territory.from_database(main_db, id=2)

print(table_info_text_list(t))

# for key, value in t.__dict__.items():
#     anno = str(t.__annotations__[key]).removeprefix("<").removesuffix(">").split("'")
#     ref_instance = anno[0].strip()
#     class_name = anno[1].strip()
#     if ref_instance == "enum":
#         enum = get_enum(class_name, value)
#         print(
#             key, enum, type(enum)
#         )

