from py_base import arislena_dice

class FixerConditionDice(arislena_dice.Nonahedron):
    """
    해결사 주사위\n
    Dice 객체를 받아 특정 등급을 묶어 확장된 판정을 만드는 클래스\n
    일체의 mod(modify)가 적용되지 않음\n
    """

    def __init__(self, extended_grade_distribution:list, extended_judge_list:list, dice_mod:int):
        """
        dice: arislena_dice.Dice 객체\n
        extended_grade_distribution: 확장된 등급 분포\n
        extended_judge_list: 확장된 판정 리스트\n
        """
        super().__init__(dice_mod)
        self.extended_grade_distribution = extended_grade_distribution
        self.extended_judge_list = extended_judge_list
        
        self.last_extended_grade = None
        self.last_extended_judge = None

        self.comparable = False
        
        self.extended_grade_table = arislena_dice.make_grade_table(extended_grade_distribution, self.grade_min)
        self.extended_judge_table = arislena_dice.make_judge_table(extended_judge_list)
    
    def roll(self, immediate_dice_mod:int=0):
        super().roll(immediate_dice_mod)
        self.last_extended_grade = self.get_extended_grade()
        self.last_extended_judge = self.get_extended_judge()

    def get_extended_grade(self):
        
        grade_result = 0
        for grade, num_range in self.extended_grade_table.items():
            if num_range[0] <= self.last_grade <= num_range[1]:
                grade_result = grade
                break
        
        return int(grade_result)

    def get_extended_judge(self):
        
        return self.extended_judge_table[str(self.last_extended_grade)]

class SentryCondition(FixerConditionDice):

    category = "초소 상태"

    def __init__(self, dice_mod:int):
        super().__init__(
            [1, 2, 1],
            ["처참한 초소", "기본적인 초소", "대비된 초소"],
            dice_mod
        )

class SuppressionUnitCondition(FixerConditionDice):

    category = "토벌대 상태"

    def __init__(self, dice_mod:int):
        super().__init__(
            [2, 1, 1],
            ["잡졸들", "토벌대", "정예 토벌대"],
            dice_mod
        )

class DefenseUnitCondition(FixerConditionDice):

    category = "수비대 상태"

    def __init__(self, dice_mod:int):
        super().__init__(
            [2, 1, 1],
            ["잡졸들", "수비대", "근위대"],
            dice_mod
        )

class PatrolUnitCondition(FixerConditionDice):
    
    category = "순찰대 상태"

    def __init__(self, dice_mod:int):
        super().__init__(
            [1, 1, 2],
            ["잡졸들", "순찰대", "사절단"],
            dice_mod
        )

class SettlementOrderCondition(FixerConditionDice):

    category = "정착지 치안 상태"

    def __init__(self, dice_mod:int):
        super().__init__(
            [1, 2, 1],
            ["문제가 이미 진행중", "문제가 최근에 적발됨", "문제가 일어남을 예측함"],
            dice_mod
        )

class ReinforcementCondition(FixerConditionDice):

    category = "증원대 상태"

    def __init__(self, dice_mod:int):
        super().__init__(
            [2, 2],
            ["구조대(하)", "증원대(중)"],
            dice_mod
        )

class CiviliansCondition(FixerConditionDice):

    category = "서민/궁중 상태"

    def __init__(self, dice_mod:int):
        super().__init__(
            [3, 1],
            ["빈곤함(하)", "부유함(상)"],
            dice_mod
        )

arislena_dice.indipendent_dice_list.extend(FixerConditionDice.__subclasses__())