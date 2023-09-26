"""
주사위 모듈
"""
import random
from copy import deepcopy

def make_grade_table(grade_distribution:list, dice_min:int, grade_min:int=0):
    """
    grade_distribution과 grade_mod를 기반으로 grade_table을 생성\n
    grade_table은 {등급: [최소 숫자, 최대 숫자]} 형식의 딕셔너리
    """

    grade_table = {}
    count = dice_min
    for grade, num in enumerate(grade_distribution, start=grade_min):
        grade_table[str(grade)] = [count, count + num - 1]
        count += num
    
    return grade_table

def make_judge_table(judge_list:list, grade_min:int=0):
    """
    judge_list를 기반으로 judge_table을 생성\n
    judge_table은 {등급: 판정 텍스트} 형식의 딕셔너리
    """

    judge_table = {}
    for grade, judge in enumerate(judge_list, start=grade_min):
        judge_table[str(grade)] = judge
    
    return judge_table

class Dice:
    """
    기본 주사위 클래스
    ---
    category : 주사위 종류\n
    """
    category = ""

    # 설정 명령어로 수정 가능한 변수의 딕셔너리
    variables_kr_en = {
        "최소 숫자" : "dice_min",
        "최대 숫자" : "dice_max",
        "눈 보정치" : "dice_mod",
        "등급 보정치" : "grade_mod",
        "이름" : "name"}

    def __init__(
            self, 
            dice_min:int, dice_max:int, 
            grade_distribution:list,
            judge_list:list,
            dice_mod:int):
        """
        dice_min : 주사위 최소 숫자\n
        dice_max : 주사위 최대 숫자\n
        grade_distribution : 등급값에 대한 주사위 숫자 분포\n
        judge_list : 등급에 대한 판정 텍스트 리스트\n
        dice_mod : 주사위 숫자에 더해질 값\n
        grade_mod : 등급값에 더해질 값\n
        ---
        last_roll : 마지막으로 굴린 주사위 숫자\n
        last_grade : 마지막으로 굴린 주사위 등급\n
        last_judge : 마지막으로 굴린 주사위 판정\n
        ---
        grade_table : 주사위 숫자에 따른 등급 테이블\n
            key : 등급값. 기본적으로 0부터 시작하여 1씩 증가함.\n
            value : 주사위 숫자 범위. [최소 숫자, 최대 숫자] 형식의 리스트\n
        judge_table : 등급에 따른 판정 텍스트 테이블\n
            key : grade_table의 key와 동일함\n
            value : 판정 텍스트. judge_list의 원소를, grade가 작은 순서부터 하나씩 입력함.\n
        ---
        예시) 6면체 주사위. 주사위 눈을 3단계로 나누고, 각 단계에 2개의 원소가 들어가며, 그 세 단계를 각각 "하", "중", "상"으로 명명하는 경우\n
        grade_distribution = [2, 2, 2]\n
        judge_list = ["하", "중", "상"]\n
        이에 따라 grade_table과 judge_table은 다음과 같이 생성됨.
        grade_table = {0: [1, 2], 1: [3, 4], 2: [5, 6]}\n
        judge_table = {0: "하", 1: "중", 2: "상"}\n
        ---
        예시) 6면체 주사위. dice_mod가 1인 경우\n
        roll()하여 1이 나오면 2로, 2가 나오면 3으로, ..., 5가 나오면 6이 됨.\n
        6이 나오면, 최댓값이 6이므로 6이 나온 것으로 간주함.\n
        ---
        예시) 6면체 주사위. grade_mod가 1인 경우\n
        roll()하여 grade가 0이 나오면 1로, 1이 나오면 2로 간주함.\n
        단, 최댓값이나 최솟값을 넘을 수는 없음.
        """
        self.dice_min = dice_min
        self.dice_max = dice_max
        self.grade_distribution = grade_distribution
        self.judge_list = judge_list
        self.dice_mod = dice_mod
        self.grade_mod = 0

        self.name:str = None
        self.grade_min = 0
        self.grade_table:dict[str, list[int]] = {}
        self.judge_table:dict[str, str] = {}
        self.last_roll = None
        self.last_grade = None
        self.last_judge = None
        self.last_gap = None

        self.comparable = True
        self.category = self.__class__.category

        if len(self.grade_distribution) > 0: self.make_grade_table()
        if len(self.judge_list) > 0: self.make_judge_table()

    def __repr__(self):
        # eval()로 다시 객체를 생성할 수 있도록 함
        return f"{self.__class__.__name__}('{self.category}', {self.dice_min}, {self.dice_max}, {self.grade_distribution}, {self.judge_list}, {self.dice_mod}, {self.grade_mod})"
    
    @classmethod
    def from_dice_data(cls, dice_data:dict):
        """
        dict 형태로 보존된 데이터를 붙여 넣은 객체를 생성함
        """
        dice = cls()
        for key, value in dice_data.items():
            setattr(dice, key, value)
        return dice

    def set_name(self, name:str):
        self.name = name

    def make_grade_table(self):
        """
        grade_distribution과 grade_mod를 기반으로 grade_table을 생성\n
        grade_table은 {등급: [최소 숫자, 최대 숫자]} 형식의 딕셔너리
        """
        self.grade_table = make_grade_table(self.grade_distribution, self.dice_min, self.grade_min)

        # count = self.dice_min
        # for grade, num in enumerate(self.grade_distribution, start=self.grade_min):
        #     self.grade_table[grade] = [count, count + num - 1]
        #     count += num

    def make_judge_table(self):
        """
        judge_list를 기반으로 judge_table을 생성\n
        judge_table은 {등급: 판정 텍스트} 형식의 딕셔너리
        """
        self.judge_table = make_judge_table(self.judge_list, self.grade_min)

        # for grade, judge in enumerate(self.judge_list, start=self.grade_min):
        #     self.judge_table[grade] = judge
    
    def resize_grade(self, grade_expand, grade_reduce, value):
        """
        grade_expand : 범위를 늘릴 등급\n
        grade_reduce : 범위를 줄일 등급\n
        value : 범위를 늘리고 줄일 값\n
        """
        self.grade_distribution[grade_expand] += value
        self.grade_distribution[grade_reduce] -= value
        self.make_grade_table()

    def check_grade_table(self):
        if len(self.grade_table) == 0: return False
        else: return True
    
    def check_judge_table(self):
        if len(self.judge_table) == 0: return False
        else: return True
    
    def adjust(self, value, min_value, max_value):
        """
        value가 min_value보다 작으면 min_value로, max_value보다 크면 max_value로 보정\n
        """
        value = max(value, min_value)
        value = min(value, max_value)
        return value

    def roll(self, immediate_dice_mod:int=0) -> str:
        """
        주사위를 굴리고, 그 숫자를 반환\n
        보정값이 적용된 주사위 눈은 정해진 범위를 벗어나지 않음\n
        last_roll last_grade, last_judge가 갱신됨\n
        return: **주사위 눈**(+ 보정값)*(+ 즉시 보정값)*\n
        """
        self.last_roll = random.randint(self.dice_min, self.dice_max) + self.dice_mod + immediate_dice_mod
        self.last_roll = self.adjust(self.last_roll, self.dice_min, self.dice_max)
        self.last_grade = self.get_grade()
        self.last_judge = self.get_judge()
        return f"**{self.last_roll}**(+ {self.dice_mod})*(+ {immediate_dice_mod})*"
    
    def get_grade(self) -> int:
        """
        self.grade_table에 따라 주사위 숫자에 해당하는 등급을 반환\n
        grade_table은 {등급: [최소 숫자, 최대 숫자]} 형식의 딕셔너리여야 함\n
        """
        if not self.check_grade_table(): return

        grade_result = 0
        for grade, num_range in self.grade_table.items():
            if num_range[0] <= self.last_roll <= num_range[1]: grade_result = grade
        
        if self.grade_mod != 0:
            grade_result = self.adjust(grade_result + self.grade_mod, self.grade_min, len(self.grade_table) - 1)
        
        return int(grade_result)
    
    def get_judge(self) -> str | None:
        """
        주사위 숫자에 따른 판정을 반환\n
        """
        if not self.check_judge_table(): return
        if self.last_grade is None: return 
        return self.judge_table[str(self.last_grade)]

    def compare_gap(self, other_dice):
        """
        이미 굴려진 주사위(다른 Dice류 객체)와 비교하여, 두 주사위의 grade 차이와 우위를 저장\n
        """
        gap = 0

        if type(other_dice) != type(self): raise TypeError("비교 대상이 주사위가 아닙니다!")

        self.check_grade_table()
        other_dice.check_grade_table()

        if self.last_grade == other_dice.last_grade and self.last_roll != other_dice.last_roll: gap = 0.5
        else: gap = self.last_grade - other_dice.last_grade

        self.last_gap = gap

    def compare_gap_str(self, other_dice) -> str:
        """
        주사위 비교 결과를 문자열로 반환\n
        반환 양식은 'n단계 격차 ({우세한 주사위 이름} 우세)'\n
        n이 0일 경우 '격차 없음'
        """
        self.compare_gap(other_dice)
        gap = abs(self.last_gap)
        superior_dice = self if self.last_grade > other_dice.last_grade else other_dice
        if gap == 0: return "격차 없음"
        else: return f"{gap}단계 격차 ({superior_dice.name} 우세)"

class Nonahedron(Dice):
    """
    9면체 주사위
    ---
    last_roll : 마지막으로 굴린 주사위 숫자\n
    last_grade : 마지막으로 굴린 주사위 숫자의 등급\n
    ---
    roll() 메서드로 주사위를 굴리면, last_roll과 last_grade가 갱신됨\n
    """
    category = "이벤트(9면체)"

    variables_kr_en = deepcopy(Dice.variables_kr_en)
    variables_kr_en["고점 중시 티어 분류(통제력, 습득력, 기만력)"] = "h_tier"
    variables_kr_en["저점 극복 티어 분류(분담력, 저지력, 회피력, 유화력)"] = "l_tier"
    variables_kr_en["안정 중시 티어 분류(돌파력, 은폐력)"] = "s_tier"

    def __init__(self, dice_mod:int=0):
        """
        mod : 주사위 숫자에 더해질 값\n
        """
        super().__init__(
            1, 9,
            [3, 3, 2, 1],
            ["처참함", "무난함", "성공", "멋지게 성공!"],
            dice_mod
        )
        self.h_tier = None
        self.l_tier = None
        self.s_tier = None

    def apply_tier(self):
        """
        아래 효과를 적용해 주사위를 재조정함\n
        ---
        H_tier:\n
        티어 1 - 주사위 8을 멋지게 성공으로 판정한다.\n
        티어 2 - 주사위 7, 8을 멋지게 성공으로 판정한다.\n
        ---
        L_tier:\n
        티어 1 - 주사위 3을 무난함으로 판정한다.\n
        티어 2 - 처참함을 무난함으로 판정한다.\n
        ---
        S_tier:\n
        티어 1 - 주사위 6을 성공으로 판정한다.\n
        티어 2 - 주사위 5, 6을 성공으로 판정한다.\n
        티어 3 - 무난함을 성공으로 판정한다.\n
        """
        if self.h_tier == 1:
            self.resize_grade(3, 2, 1)
        elif self.h_tier == 2:
            self.resize_grade(3, 2, 2)
        
        if self.l_tier == 1:
            self.resize_grade(1, 0, 1)
        elif self.l_tier == 2:
            self.resize_grade(1, 0, 3)
        
        if self.s_tier == 1:
            self.resize_grade(2, 1, 1)
        elif self.s_tier == 2:
            self.resize_grade(2, 1, 2)
        elif self.s_tier == 3:
            self.resize_grade(2, 1, 3)

class AdvantageDice(Nonahedron):

    category = "총분석 주사위"

    text_dict = {
        "-3" : "",
        "-2" : "",
        "-1" : "",
        "1" : "",
        "2" : "",
        "3" : ""
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)
    
    def compare_gap_str(self, other_dice) -> str:
        """
        **override**
        격차 문자열 형식: 양/음 N단계 격차
        """
        self.compare_gap(other_dice)
        if -1 < self.last_gap < 1: return "격차 없음"
        elif self.last_gap >= 1: return f"양 {self.last_gap}단계 격차"
        else: return f"음 {self.last_gap}단계 격차"
    
    def get_text(self) -> str | None:
        """
        gap에 따른 텍스트 반환
        """
        try:
            return self.__class__.text_dict[str(self.last_gap)]
        except KeyError:
            return "눈에 띄는 격차가 없습니다."

class ScaleAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "우린 한줌 모래애 불과합니다. 희망이 없습니다.",
        "-2" : "적은 우리보다 명백히 많습니다.",
        "-1" : "실수해서는 안됩니다. 적은 우리보다 많습니다.",
        "1" : "적은 우리보다 적습니다.",
        "2" : "적은 고작 한줌의 모래 같이 보입니다.",
        "3" : "적은 고작 한줌의 모래 같이 보이며 그마저 뒷걸음질 칩니다!"
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class MovementAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "우리의 움직임이 스스로의 균형을 무너뜨렸고, 통제가 강화됩니다.",
        "-2" : "우리의 움직임이 스스로의 균형을 무너뜨렸고, 통제가 강화됩니다.",
        "-1" : "적들을 피해 움직이는 건 무리였습니다.",
        "1" : "적들의 방해를 간신히 피했습니다.",
        "2" : "적들은 우리를 통제하지 못합니다.",
        "3" : "적들은 완전히 발이 묶였고 우리는 자유롭습니다."
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)


class AuthorityAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "그들은 우리의 권위를 벌레 껍질만 못하다고 생각합니다.",
        "-2" : "그들은 우리를 자기들의 종인 것처럼 대합니다.",
        "-1" : "그들은 우리의 권위에 대해 그다지 신경쓰지 않습니다.",
        "1" : "그들은 우리의 권위를 존중합니다.",
        "2" : "우리는 그들의 가장 중요한 손님입니다.",
        "3" : "그들은 마치 그들이 우리의 종인 듯 복종합니다."
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class MoralAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "병사들은 의지를 잃었습니다.",
        "-2" : "병사들은 겁에 질렸습니다.",
        "-1" : "병사들에게는 확신이 없습니다.",
        "1" : "병사들은 직접적인 이점을 통해 자신감을 다졌습니다.",
        "2" : "병사들에게 특별한 동기가 주어졌습니다.",
        "3" : "\"우리의 결속은 견고하다. 우리의 맹세는 둔중하다. 우리의 결의는 확고하다. 우리의 목적은 명백하다!\""
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class EquipmentAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "우리가 보유한 장비 대부분이 고장나고 파손되었습니다.",
        "-2" : "장비 몇몇이 고장나고 파손되어 나머지 인원들이 일이 없어 바닥이나 쓸며 놀 지경입니다.",
        "-1" : "그들의 장비가 우리 장비보다 낫습니다.",
        "1" : "우리 장비가 그들의 장비보다 낫습니다.",
        "2" : "그들의 장비는 저열합니다. 그런 장비로 일하다니 불쌍해보일 지경입니다.",
        "3" : "그들은 거의 맨몸 수준이나 다를 바 없는 쓰레기 같은 장비만을 갖췄습니다."
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class LandformAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "터가 틀렸습니다. 여기 있으면 안됩니다.",
        "-2" : "이제라도 위치를 옮기는게 나을 것입니다. 이대로는 불리합니다.",
        "-1" : "저들이 고지를 선점했습니다.",
        "1" : "우리는 고지를 선점했습니다.",
        "2" : "우리가 하는 일을 방해하려면 대단한 노력이 필요할 것입니다.",
        "3" : "어떠한 물리력도 우리를 방해할 수 없습니다. 우린 하늘 위에 있는 것이나 다름없습니다."
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)
        
class FundAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "우리 재정 상태를 고려했을 때, 이 거래는 비상식적이고 터무니 없습니다.",
        "-2" : "우리는 그들의 요구에 맞춰줄 재정적 여유가 없습니다.",
        "-1" : "우리는 아쉽게도 그 거래를 치를 수 없습니다.",
        "1" : "그 거래를 마치고 난 뒤 근소한 여유가 남습니다.",
        "2" : "",
        "3" : ""
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class SupplyAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "",
        "-2" : "우리 탄환이 적들의 머릿수보다 부족합니다.",
        "-1" : "늘 그렇듯 뭔가 항상 부족합니다.",
        "1" : "다행히 크게 부족한 것 없습니다.",
        "2" : "우리는 풍족합니다.",
        "3" : "얼마든 쏟아부어도 괜찮습니다. 우리 보급관은 최고거든요."
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class PublicopinionAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "여기 있으면 안됩니다.",
        "-2" : "분위기가 적대적입니다.",
        "-1" : "뭔가 사소한 실수가 벌어진 듯 합니다.",
        "1" : "사람들은 우리의 행동에 온정적입니다.",
        "2" : "우리 행동은 여론의 강력한 지지를 받습니다.",
        "3" : "하늘이 우리 편입니다."
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class TrainAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "저들은 악명높은 존재들이며, 그 사실을 우리 사람들 하나하나가 다 알고 있습니다.",
        "-2" : "저들은 악명높은 존재들입니다.",
        "-1" : "저것들 좀 겁납니다.",
        "1" : "우리가 저것들보다 후달릴 게 뭡니까? 붙어보고 이야기합시다.",
        "2" : "우리는 잘 훈련되었습니다.",
        "3" : "저것들은 우리들에 비하면 갓난아기들이나 다름없습니다. 얼른 쳐부수고 끝장봅시다."
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class StrategyAdvantage(AdvantageDice):

    text_dict = {
        "-3" : "적들이 허를 찔러 들어옵니다.",
        "-2" : "적들이 우리의 허실을 읽었습니다.",
        "-1" : "미처 대비하지 못한 문제들이 있습니다.",
        "1" : "준비에 부족함 없습니다.",
        "2" : "계획은 완벽합니다. 크게 뒤틀리지 않길 바랄 뿐입니다.",
        "3" : "모든 것은 계획대로고 적들은 바보멍청이입니다."
    }

    def __init__(self, dice_mod:int):
        super().__init__(dice_mod)

class Birth(Dice):
    """
    출산 주사위 묶음
    """

    category = "출산"

    # Dice와 같은 __init__ 파라미터
    def __init__(self, dice_min:int, dice_max:int, grade_distribution:dict, judge_list:list, dice_mod:int):
        super().__init__(dice_min, dice_max, grade_distribution, judge_list, dice_mod)

    
class Birth1(Birth):
    """
    첫 번째 출산 주사위\n
    0, 1의 범위를 가지며 0이면 사망, 1이면 생존
    """
    category = "생존여부"

    def __init__(self, dice_mod:int):

        super().__init__(
            0, 1,
            [1, 1],
            ["사망", "생존"],
            dice_mod
        )

class Birth2(Birth):
    """
    두 번째 출산 주사위\n
    출산 후 산모의 건강 상태 경과를 나타냄\n
    1~7이면 사망, 8~25면 영구한 후유증, 26~100이면 안전
    """
    category = "출산 후 산모 건강 상태"
    
    def __init__(self, dice_mod:int):
        super().__init__(
            1, 100,
            [7, 18, 75],
            ["사망", "영구한 후유증", "안전"],
            dice_mod
        )


class Birth3(Birth):
    """
    세 번째 출산 주사위\n
    산아가 어떻게 이루어졌는지를 판정함\n
    1인 경우: 여성/남성 이란성 쌍둥이\n
    2인 경우: 남성/여성 이란성 쌍둥이\n
    3~4인 경우: 남성/남성 이란성 쌍둥이\n
    5~6인 경우: 여성/여성 이란성 쌍둥이\n
    7~8인 경우: 남성/남성 일란성 쌍둥이\n
    9~10인 경우: 여성/여성 일란성 쌍둥이\n
    11~56인 경우: 남성\n
    57~100인 경우: 여성
    """
    category = "산아 형태"

    def __init__(self, dice_mod:int):
        super().__init__(
            1, 100,
            [2, 4, 2, 2, 2, 2, 46, 44],
            ["여성/남성 이란성 쌍둥이", "남성/여성 이란성 쌍둥이", "남성/남성 이란성 쌍둥이", "여성/여성 이란성 쌍둥이", "남성/남성 일란성 쌍둥이", "여성/여성 일란성 쌍둥이", "남성", "여성"],
            dice_mod
        )

class Birth4(Birth):
    """
    네 번째 출산 주사위\n
    태어난 아이의 외모 상태를 판정함\n
    1~3인 경우: 빼어남\n
    4~11인 경우: 잘생김\n
    12~95인 경우: 평범함\n
    96~100인 경우: 섬뜩함
    """
    category = "태아 외모"
    
    def __init__(self, dice_mod:int):
        super().__init__(
            1, 100,
            [3, 8, 84, 5],
            ["빼어남", "잘생김", "평범함", "섬뜩함"],
            dice_mod
        )

class Birth5(Birth):
    """
    다섯 번째 출산 주사위\n
    태어난 아이의 건강 상태를 판정함\n
    1~77인 경우: 무난함\n
    78~94인 경우: 잔병치레\n
    95~100인 경우: 선천적 장애인
    """
    category = "태아 건강"
    
    def __init__(self, dice_mod:int):
        super().__init__(
            1, 100,
            [77, 17, 6],
            ["무난함", "잔병치레", "선천적 장애인"],
            dice_mod
        )

class Birth6(Birth):
    """
    여섯 번째 출산 주사위\n
    태어난 아이의 수명을 판정함\n
    이 주사위는 grade와 judge table이 없는 1~50 범위의 평범한 주사위임
    """
    category = "태아 수명"
    
    def __init__(self, dice_mod:int):
        super().__init__(
            1, 50,
            [],
            [],
            dice_mod
        )

class Birth7(Birth):
    """
    일곱 번째 출산 주사위\n
    태어난 아이의 사인을 판정함\n
    1인 경우: 음독
    2인 경우: 익사
    3인 경우: 낙사
    4인 경우: 분사
    5인 경우: 병사
    6인 경우: 전사
    7인 경우: 아사
    8인 경우: 의문사 혹은 자연사
    9인 경우: 돌연사
    10인 경우: 자살
    """
    category = "미래의 사인"

    def __init__(self, dice_mod:int):
        super().__init__(
            1, 10,
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            ["음독", "익사", "낙사", "분사", "병사", "전사", "아사", "의문사 혹은 자연사", "돌연사", "자살"],
            dice_mod
        )

class EnvironmentDice(Dice):
    """
    환경 주사위 (빈 클래스)
    """

    category = "환경"
    
    def __init__(self, judge_list:list, dice_mod:int):
        super().__init__(1, 4, [1, 1, 1, 1], judge_list, dice_mod)

class WeatherDice(EnvironmentDice):
    """
    날씨 주사위
    """

    category = "날씨"
    def __init__(self, dice_mod:int):
        super().__init__(
            ["건조", "소나기", "강우/강설", "안개"],
            dice_mod
        )

class SeasonDice(EnvironmentDice):
    """
    계절 주사위
    """

    category = "계절"
    def __init__(self, dice_mod:int):
        super().__init__(
            ["봄", "여름", "가을", "겨울"],
            dice_mod
        )

class TimeDice(EnvironmentDice):
    """
    시간대 주사위
    """

    category = "시간대"
    def __init__(self, dice_mod:int):
        super().__init__(
            ["새벽", "낮", "저녁", "밤"],
            dice_mod
        )

# 독립적으로 사용할 수 있는 주사위 리스트
indipendent_dice_list:list[Dice] = []
# 묶음으로만 사용할 수 있는 주사위 리스트 (추상적 클래스)
group_only_dice_list:list[Dice] = []

indipendent_dice_list.extend([Nonahedron])
group_only_dice_list.extend([Birth, EnvironmentDice, AdvantageDice])