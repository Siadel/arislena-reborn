"""
게임 요소를 칭하는 한국어와 시스템 버전의 딕셔너리를 모은 모듈
"""
from py import enums, utility

# 파이썬과 sql 데이터 형식 딕셔너리
datatype_dict = {
            str: "TEXT",
            int: "INTEGER",
            float: "REAL"
        }

# 군사 카테고리 한국어-영어 딕셔너리
mil_category = {
    "군사": "soldier",
    "전차": "chariot",
    "공성구": "siege_equipment",
    "장군": "general"
}
mil_category_swap = utility.swap_dict(mil_category)
# 자원 카테고리 한국어-영어 딕셔너리
res_category = {
    "식량": "food",
    "자재": "material",
    "군수품" : "supply",
    "사치품" : "luxury"
}

# 블럭 상태 숫자 - 한국어 딕셔너리
block_status = {
    enums.Block.SAFE: "안전",
    enums.Block.CRISIS: "위기"
}
# 부대 상태 숫자 - 한국어 딕셔너리
troop_status = {
    enums.Troop.IDLE: "대기",
    enums.Troop.ALERT: "경계",
    enums.Troop.MOVING: "이동",
    enums.Troop.FORTIFYING: "요새화"
}

# 외교 극성 숫자 - 한국어 딕셔너리
diplomacy_polarity = {
    -1: "부정적",
    0: "중립적",
    1: "긍정적"
}
# 나라 설정 데이터 영어 - 한국어 딕셔너리
nation_extras = {
    "nation_name" : "국가 이름",
    "leader" : "지도자",
    "religion" : "종교",
    "ethos" : "국가 키워드",
    "concern" : "국가 관심사",
    "foundation_story" : "건국 이야기",
    "extra" : "기타"
}
nation_extras_swap = utility.swap_dict(nation_extras)

# 나라 변수 영어-한국어 딕셔너리
nation_variable_dict = {
    "ID": "아이디",
    "owner_ID": "오너 아이디",
    "owner": "오너",
    "name": "이름",
    "race": "종족",
    "settle_point": "개척 포인트",
    "food": "식량",
    "material": "자재",
    "supply": "군수품",
    "luxury": "사치품",
    "fate": "숙명",
    "immune": "남은 무적 턴",
}
nation_variable_dict_swap = utility.swap_dict(nation_variable_dict)
# 블럭 변수 영어-한국어 딕셔너리
block_variable_dict = {
    "ID": "아이디",
    "nation_ID": "나라 아이디",
    "name": "이름",
    "category": "카테고리",
    "level": "레벨",
    "food_yield": "식량 생산량",
    "material_yield": "자재 생산량",
    "military_scale_cap": "최대 부대 규모 증가량",
    "frontline_cap": "최대 전선 규모",
    "power_modifier": "방어 시 전투력 증가량",
    "status": "상태"
}
block_variable_dict_swap = utility.swap_dict(block_variable_dict)
# 부대 변수 영어-한국어 딕셔너리
troop_variable_dict = {
    "ID": "아이디",
    "nation_ID": "나라 아이디",
    "location": "부대 위치",
    "name": "이름",
    "soldier": "군사 수",
    "general": "장군 수",
    "chariot": "전차 수",
    "siege_equipment": "공성구 수",
    "status": "상태",
    "attacked": "공격한 횟수"
}
# 외교 변수 영어-한국어 딕셔너리
diplomacy_variable_dict = {
    "ID": "아이디",
    "category": "카테고리",
    "departure": "출발 나라 아이디",
    "destination": "도착 나라 아이디",
    "expire": "만료 턴"
}
# 테이블 영어-한국어 딕셔너리
table_dict = {
    "nation": "나라",
    "block" : "블럭",
    "troop" : "부대",
    "diplomacy" : "외교"
}
# 딕셔너리로 가는 딕셔너리
variable_dict_dict = {
    "nation": nation_variable_dict,
    "block": block_variable_dict,
    "troop": troop_variable_dict,
    "diplomacy": diplomacy_variable_dict
}