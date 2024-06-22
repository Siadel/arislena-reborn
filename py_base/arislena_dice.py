"""
주사위 모듈
"""
import random
from copy import deepcopy
from typing import Any

from py_base.abstract import ArislenaEnum
from py_base.ari_enum import NonahedronJudge

def adjust(value, min_value, max_value) -> int:
    """
    value가 min_value보다 작으면 min_value로, max_value보다 크면 max_value로 보정\n
    """
    value = min(value, max_value)
    value = max(value, min_value)
    return value

class DiceOption:
    
    def __init__(self):
        self.enable_min_cap = True
        self.enable_max_cap = True

class Dice:
    """
    기본 주사위 클래스
    ---
    category : 주사위 종류\n
    """
    category = ""

    def __init__(
        self, 
        dice_min: int, 
        dice_max: int, 
        grade_distribution: list,
        judge_enum: list[ArislenaEnum],
        dice_mod: int,
        grade_mod: int
    ):
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
        ```
        grade_distribution = [2, 2, 2]
        judge_list = ["하", "중", "상"]
        ```
        이에 따라 grade_table과 judge_table은 다음과 같이 생성됨.
        ```
        grade_table = {0: [1, 2], 1: [3, 4], 2: [5, 6]}
        judge_table = {0: "하", 1: "중", 2: "상"}
        ```
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
        self._grade_distribution = grade_distribution
        self._judge_enum = judge_enum
        self._dice_mod = dice_mod
        self._grade_mod = grade_mod

        self.name:str = None
        self.option:DiceOption = DiceOption()
        self._grade_min = 0
        self._grade_table:dict[str, list[int]] = {}
        self._last_roll: int = None
        self._last_grade = None
        self._last_judge = None

        if len(self._grade_distribution) > 0: self._make_grade_table()
        
    def __str__(self):
        rtn_str = f"[{self.get_judge}] **{self._last_roll}**"
        if self._dice_mod != 0: rtn_str += f" (+ {self._dice_mod})"
        return rtn_str

    def __repr__(self):
        # eval()로 다시 객체를 생성할 수 있도록 함
        return f"{self.__class__.__name__}('{self.category}', {self.dice_min}, {self.dice_max}, {self._grade_distribution}, {self._judge_enum}, {self._dice_mod}, {self._grade_mod})"
    
    def __lt__(self, other: "Dice"):
        self._check_same_type_or_raise(other)
        return self._last_roll < other._last_roll
    
    def __gt__(self, other: "Dice"):
        self._check_same_type_or_raise(other)
        return self._last_roll > other._last_roll
    
    def __le__(self, other: "Dice"):
        self._check_same_type_or_raise(other)
        return self._last_roll <= other._last_roll
    
    def __ge__(self, other: "Dice"):
        self._check_same_type_or_raise(other)
        return self._last_roll >= other._last_roll
    
    def __eq__(self, other: "Dice"):
        self._check_same_type_or_raise(other)
        return self._last_roll == other._last_roll
    
    def __ne__(self, other: "Dice"):
        self._check_same_type_or_raise(other)
        return self._last_roll != other._last_roll
    
    def __mul__(self, other: int):
        return sum(self.roll_multiple_times(other))
    
    @property
    def grade_table(self):
        return self._grade_table
    
    @property
    def last_roll(self):
        return self._last_roll
    
    @property
    def last_grade(self):
        return self._last_grade
    
    @property
    def last_judge(self):
        return self._last_judge
    
    @classmethod
    def from_dice_data(cls, dice_data:dict):
        """
        dict 형태로 보존된 데이터를 붙여 넣은 객체를 생성함
        """
        dice = cls()
        for key, value in dice_data.items():
            setattr(dice, key, value)
        return dice
    
    def _check_same_type_or_raise(self, other: Any):
        if type(other) != type(self): raise TypeError("같은 타입의 주사위만 비교할 수 있습니다.")

    def _make_grade_table(self):
        """
        grade_distribution과 grade_mod를 기반으로 grade_table을 생성\n
        grade_table은 {등급: [최소 숫자, 최대 숫자]} 형식의 딕셔너리
        """

        grade_table = {}
        count = self.dice_min
        for grade, num in enumerate(self._grade_distribution, start=self._grade_min):
            grade_table[str(grade)] = [count, count + num - 1]
            count += num
        
        self._grade_table = grade_table
        
        # count = self.dice_min
        # for grade, num in enumerate(self.grade_distribution, start=self.grade_min):
        #     self.grade_table[grade] = [count, count + num - 1]
        #     count += num
    
    def _resize_grade(self, grade_expand, grade_reduce, value):
        """
        grade_expand : 범위를 늘릴 등급\n
        grade_reduce : 범위를 줄일 등급\n
        value : 범위를 늘리고 줄일 값\n
        """
        self._grade_distribution[grade_expand] += value
        self._grade_distribution[grade_reduce] -= value
        self._make_grade_table()

    def _check_grade_table(self):
        if len(self._grade_table) == 0: return False
        else: return True
    
    def _adjust_dice(self, value) -> int:
        """
        value가 min_value보다 작으면 min_value로, max_value보다 크면 max_value로 보정\n
        """
        if self.option.enable_min_cap:
            value = min(value, self.dice_min)
        if self.option.enable_max_cap:
            value = max(value, self.dice_max)
        return value
    
    def _roll_core(self):
        return self._adjust_dice(random.randint(self.dice_min, self.dice_max) + self._dice_mod)
        
    def _update(self):
        self._last_grade = self.get_grade()
        self._last_judge = self.get_judge()

    def set_name(self, name:str):
        self.name = name
        return self
    
    def set_last_roll(self, value:int):
        """
        주사위를 굴려서 value의 값이 나온 것으로 치고, last_roll, last_grade, last_judge를 갱신함
        """
        self._last_roll = self._adjust_dice(value)
        self._update()
        return self
    
    def set_dice_mod(self, value:int):
        self._dice_mod = value
        return self
    
    def add_dice_mod(self, value:int):
        self._dice_mod += value
        return self

    def roll(self):
        """
        주사위를 굴리고, 그 숫자를 반환\n
        보정값이 적용된 주사위 눈은 정해진 범위를 벗어나지 않음\n
        last_roll last_grade, last_judge가 갱신됨\n
        
        return: 주사위 눈\n
        """
        self._last_roll = self._roll_core()
        self._update()
        return self._last_roll
    
    def roll_multiple_times(self, times: int) -> tuple[int]:
        """
        주사위를 여러 번 굴리고, 그 숫자들을 튜플로 반환\n
        """
        return (self._roll_core() for _ in range(times))
    
    def get_grade(self) -> int:
        """
        self.grade_table에 따라 주사위 숫자에 해당하는 등급을 반환\n
        grade_table은 {등급: [최소 숫자, 최대 숫자]} 형식의 딕셔너리여야 함\n
        """
        if not self._check_grade_table(): return
        if self._last_roll is None: return

        grade_result = 0
        for grade, num_range in self._grade_table.items():
            if num_range[0] <= self._last_roll <= num_range[1]: grade_result = grade
        
        if self._grade_mod != 0:
            grade_result = adjust(
                grade_result + self._grade_mod, 
                self._grade_min, 
                len(self._grade_table) - 1
            )
        
        return int(grade_result)

    def get_judge(self) -> ArislenaEnum | None:
        """
        주사위 숫자에 따른 판정(enum)을 반환\n
        """
        if self._last_grade is None: return
        return self._judge_enum[self._last_grade]



class Nonahedron(Dice):
    """
    9면체 주사위
    ---
    last_roll : 마지막으로 굴린 주사위 숫자\n
    last_grade : 마지막으로 굴린 주사위 숫자의 등급\n
    ---
    roll() 메서드로 주사위를 굴리면, last_roll과 last_grade가 갱신됨\n
    """

    def __init__(self, dice_mod:int=0, grade_mod:int=0):
        """
        mod : 주사위 숫자에 더해질 값\n
        """
        super().__init__(
            1, 9,
            [3, 3, 2, 1],
            list(NonahedronJudge),
            dice_mod,
            grade_mod
        )
    
    @property
    def last_judge(self) -> NonahedronJudge:
        return super().last_judge
    
    def get_judge(self) -> NonahedronJudge | None:
        return super().get_judge()