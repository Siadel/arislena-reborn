"""
Sql과 연동되는 데이터 클래스들
"""
from py_base import ari_enum
from py_base.datatype import ExtInt
from py_base.dbmanager import MainDB
from py_system.abstract import TableObject

def deserialize(table_name:str, data:list) -> TableObject:
    """
    sql 테이블 데이터에서 불러온 데이터를 이곳에 구현된 클래스로 변환하는 함수\n
    자료형이 ExtInt인 경우, ExtInt에 데이터의 int값을 더해서 반환함 (기본적으로 ExtInt는 0으로 초기화됨)
    주의: 이 함수는 **반드시** py_system.tableobj 모듈에 있어야 함
    """
    # table_name의 첫 글자를 대문자로 바꿔서 클래스 이름으로 사용
    table_name = table_name[0].upper() + table_name[1:]
    tableobj:TableObject = globals()[table_name]()
    for key, value in zip(tableobj.items.keys(), data):

        if "ExtInt" in str(tableobj.__annotations__[key]):
            tableobj.__setattr__(key, tableobj.__getattribute__(key) + value)
        else:
            tableobj.__setattr__(key, value)
        # if not isinstance(value, int):
        #     tableobj.__setattr__(key, value)
        # else:
        #     if "ExtInt" in str(tableobj.__annotations__[key]):
        #         tableobj.__setattr__(key, tableobj.__getattribute__(key) + value)
        #     else:
        #         tableobj.__setattr__(key, value)
    return tableobj

def form_database_from_tableobjects(main_db:MainDB):
    """
    TableObject 객체를 상속하는 객체의 수만큼 테이블 생성하고, 테이블을 초기화
    만약 TableObject를 상속하는 객체의 데이터 형식이 기존의 데이터 형식과 다를 경우, 기존의 데이터를 유지하며 새로운 데이터 형식을 추가
    """
    for subclass in TableObject.__subclasses__():
        # TableObject를 상속하는 객체의 테이블을 생성함 (이미 존재할 경우, 무시함)
        subclass = subclass()
        main_db.cursor.execute(subclass.get_create_table_string())

        table_name = subclass.table_name
        # TableObject를 상속하는 객체의 데이터 형식과 main_db의 데이터 형식을 불러와 차이를 판별하기
        # main_db의 데이터 형식을 불러옴
        sql_table_column_set = main_db.table_column_set(table_name)

        # TableObject를 상속하는 객체의 데이터 형식을 불러옴
        tableobj_column_set = subclass.column_set

        # 데이터베이스 테이블의 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교함
        # TableObject를 상속하는 객체에 없는 데이터 형식이 있을 경우, main_db에서 해당 데이터 형식을 삭제함
        for column_name in (sql_table_column_set - tableobj_column_set):
            main_db.cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
        # main_db에 없는 데이터 형식이 있을 경우, main_db에 해당 데이터 형식을 추가함
        for column_name in (tableobj_column_set - sql_table_column_set):
            main_db.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {subclass.get_column_type(column_name)}")
        
        # 데이터베이스 테이블의 데이터 형식을 다시 불러옴
        sql_table_column_set = main_db.table_column_set(table_name)
        
        # 새로 불러온 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교함
        if set(sql_table_column_set) != set(tableobj_column_set):
            has_row = main_db.has_row(table_name)
            if has_row:
                # 테이블 데이터 임시 저장
                # 테이블에 데이터가 없는 경우 임시 저장할 필요 없음
                main_db.cursor.execute(f"CREATE TABLE {table_name}_temp AS SELECT * FROM {table_name}")
            # 테이블 삭제
            main_db.cursor.execute(f"DROP TABLE {table_name}")
            # 테이블 재생성
            main_db.cursor.execute(subclass.get_create_table_string())
            if has_row:
                # 임시 저장 테이블의 column마다 작업하여 테이블 데이터 복원
                # 임시 저장 테이블의 데이터를 {key:value} 형식으로 변환함
                main_db.cursor.execute(f"SELECT * FROM {table_name}_temp")
                backup_data = [dict(zip([column[0] for column in main_db.cursor.description], data)) for data in main_db.cursor.fetchall()]
                # 임시 저장 테이블의 데이터를 새로운 테이블에 삽입함
                for data in backup_data:
                    main_db.insert(subclass(**data))
                # 임시 저장 테이블 삭제
                main_db.cursor.execute(f"DROP TABLE {table_name}_temp")
    
    print("Database initialized")

"""
!! ---------------------- 주의 ---------------------- !!

abstract variables: __slots__, display_column
abstract properties: kr_list
"""

"""
액티브 데이터
"""
class User(TableObject):

    __columns__: tuple = (
        "id",
        "discord_id",
        "discord_name",
        "register_date"
    )

    def __init__(
        self,
        id: int = 0,
        discord_id:int = 0,
        discord_name:str = "",
        register_date:str = ""
    ):
        super().__init__(id)
        self.discord_id = discord_id
        self.discord_name = discord_name
        self.register_date = register_date

        # __slots__에 추가되지 않는 속성은 여기에 추가
        self.display_column = "discord_name"
    
    @property
    def kr_list(self) -> list[str]:
        return super().kr_list.extend([
            "디스코드 아이디",
            "디스코드 이름",
            "가입일"
        ])



class Faction(TableObject):
    
    __columns__: tuple = (
        "id",
        "user_id",
        "name",
        "level"
    )

    def __init__(
        self,
        id: int = 0,
        user_id:int = 0,
        name:str = "",
        level:int = 0
    ):
        super().__init__(id)
        self.user_id = user_id
        self.name = name
        self.level = level

        # __slots__에 추가되지 않는 속성은 여기에 추가
        self.display_column = "name"
    
    @property
    def kr_list(self) -> list[str]:
        return super().kr_list.extend([
            "유저 아이디",
            "세력명",
            "레벨"
        ])

    def insert_new_territory(self):
        """
        faction을 주인으로 하는 새로운 영토 생성
        """
        # 영토 생성
        self._database.insert(
            self
        )

class FactionHierarchyNode(TableObject):

    __columns__: tuple = (
        "id",
        "higher",
        "lower"
    )

    def __init__(
        self,
        id: int = 0,
        higher:int = 0,
        lower:int = 0
    ):
        super().__init__(id)
        self.higher = higher
        self.lower = lower

        # __slots__에 추가되지 않는 속성은 여기에 추가
        self.display_column = "higher"
    
    @property
    def kr_list(self) -> list[str]:
        return super().kr_list.extend([
            "상위 세력",
            "하위 세력"
        ])
    
    def push(self, lower_fation:Faction, higher_faction:Faction):
        """
        계급 설정
        """
        if lower_fation.level > higher_faction.level:
            raise ValueError("하위 세력의 레벨이 상위 세력의 레벨보다 높습니다.")
        self.higher = higher_faction.id
        self.lower = lower_fation.id
        super().push()

    def fetch_all_high_hierarchy(self, faction:Faction) -> list[Faction]:
        """
        해당 세력의 상위 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self._database.fetch_many("FactionHierarchyNode", f"lower = {faction.id}")

        return [self._database.fetch("faction", f"ID = {node.higher}") for node in nodes]
    
    def fetch_all_low_hierarchy(self, faction:Faction) -> list[Faction]:
        """
        해당 세력의 하위 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self._database.fetch_many("FactionHierarchyNode", f"higher = {faction.id}")

        return [self._database.fetch("faction", f"ID = {node.lower}") for node in nodes]
    
    def fetch_all_hierarchy_id(self, faction:Faction) -> list[int]:
        """
        해당 세력의 계급을 모두 가져옴
        """

        nodes:list[FactionHierarchyNode] = self._database.fetch_many("FactionHierarchyNode", f"higher = {faction.id} OR lower = {faction.id}")

        return [node.id for node in nodes]


class Population(TableObject):

    __columns__: tuple = (
        "id",
        "faction_id",
        "name",
        "labor",
        "food_consumption",
        "water_consumption",
        "is_laboring"
    )

    def __init__(
        self,
        id: int = 0,
        faction_id:int = 0,
        name:str = "",
        labor:int = 1,
        food_consumption:int = 1,
        water_consumption:int = 1,
        is_laboring:int = ari_enum.YesNo.NO.value
    ):
        super().__init__(id)
        self.faction_id = faction_id
        self.name = name
        self.labor = labor
        self.food_consumption = food_consumption
        self.water_consumption = water_consumption
        self.is_laboring = is_laboring

        # __slots__에 추가되지 않는 속성은 여기에 추가
        self.display_column = "name"
    
    @property
    def kr_list(self) -> list[str]:
        return super().kr_list.extend([
            "세력 아이디",
            "이름",
            "노동력",
            "식량 소비",
            "물 소비",
            "노동 중"
        ])


class Livestock(TableObject):

    __columns__: tuple = (
        "id",
        "faction_id",
        "labor",
        "feed_consumption",
        "is_laboring"
    )

    def __init__(
        self,
        id: int = 0,
        faction_id:int = 0,
        labor:int = 1,
        feed_consumption:int = 1,
        is_laboring:int = ari_enum.YesNo.NO.value
    ):
        super().__init__(id)
        self.faction_id = faction_id
        self.labor = labor
        self.feed_consumption = feed_consumption
        self.is_laboring = is_laboring

        # __slots__에 추가되지 않는 속성은 여기에 추가
        self.display_column = "ID"
    
    @property
    def kr_list(self) -> list[str]:
        return super().kr_list.extend([
            "세력 아이디",
            "노동력",
            "식량 소비",
            "물 소비",
            "노동 중"
        ])

class Resource(TableObject):

    __columns__: tuple = (
        "id",
        "faction_id",
        "water",
        "food",
        "feed",
        "wood",
        "soil",
        "stone",
        "building_material"
    )

    def __init__(
        self,
        id: int = 0,
        faction_id:int = 0,
        water:ExtInt = ExtInt(0, min_value = 0),
        food:ExtInt = ExtInt(0, min_value = 0),
        feed:ExtInt = ExtInt(0, min_value = 0),
        wood:ExtInt = ExtInt(0, min_value = 0),
        soil:ExtInt = ExtInt(0, min_value = 0),
        stone:ExtInt = ExtInt(0, min_value = 0),
        building_material:ExtInt = ExtInt(0, min_value = 0)
    ):
        super().__init__(id)
        self.faction_id = faction_id
        self.water = water
        self.food = food
        self.feed = feed
        self.wood = wood
        self.soil = soil
        self.stone = stone
        self.building_material = building_material

        # __slots__에 추가되지 않는 속성은 여기에 추가
        self.display_column = "ID"
    
    @property
    def kr_list(self) -> list[str]:
        return super().kr_list.extend([
            "세력 아이디",
            "물",
            "식량",
            "사료",
            "목재",
            "흙",
            "건축자재"
        ])


class Territory(TableObject):

    __columns__: tuple = (
        "id",
        "faction_id",
        "name",
        "space_limit",
        "safety"
    )

    def __init__(
        self,
        id: int = 0,
        faction_id:int = 0,
        name:str = "",
        space_limit:int = 1,
        safety:int = 0
    ):
        super().__init__(id)
        self.faction_id = faction_id
        self.name = name
        self.space_limit = space_limit
        self.safety = safety

        # __slots__에 추가되지 않는 속성은 여기에 추가
        self.display_column = "name"
    
    @property
    def kr_list(self) -> list[str]:
        return super().kr_list.extend([
            "세력 아이디",
            "이름",
            "공간 제한",
            "안정도"
        ])

class Building(TableObject):

    __columns__: tuple = (
        "id",
        "territory_id",
        "discriminator",
        "name"
    )

    def __init__(
        self,
        id: int = 0,
        territory_id:int = 0,
        discriminator:int = 0,
        name:str = ""
    ):
        super().__init__(id)
        self.territory_id = territory_id
        self.discriminator = discriminator
        self.name = name

        # __slots__에 추가되지 않는 속성은 여기에 추가
        self.display_column = "name"
    
    @property
    def kr_list(self) -> list[str]:
        return super().kr_list.extend([
            "영토 아이디",
            "구분",
            "이름"
        ])


