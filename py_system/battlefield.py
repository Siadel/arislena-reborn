"""
전투 관련
"""
from typing import Iterator, ClassVar, Callable
from dataclasses import dataclass

from py_base.ari_enum import Strategy
from py_system.tableobj import Faction
from py_system.arislena_dice import Nonahedron

@dataclass
class DicePackage:
    
    scale: Nonahedron = None
    mobility: Nonahedron = None
    morale: Nonahedron = None
    
    def __str__(self) -> str:
        """
        discord embed에 사용될 수 있는 문자열을 반환한다.
        """
        return f"- 규모: {self.scale}\n- 기동: {self.mobility}\n- 사기: {self.morale}"
    
    def __iter__(self) -> Iterator[Nonahedron]:
        return iter([self.scale, self.mobility, self.morale])
    
    def __lt__(self, other: "DicePackage") -> bool:
        return sum([dice < list(other.__iter__())[i] for i, dice in enumerate(self.__iter__())]) > 1
    
    def __le__(self, other: "DicePackage") -> bool:
        return sum([dice <= list(other.__iter__())[i] for i, dice in enumerate(self.__iter__())]) > 1
    
    def __gt__(self, other: "DicePackage") -> bool:
        return sum([dice > list(other.__iter__())[i] for i, dice in enumerate(self.__iter__())]) > 1
    
    def __ge__(self, other: "DicePackage") -> bool:
        return sum([dice >= list(other.__iter__())[i] for i, dice in enumerate(self.__iter__())]) > 1
    
    def __eq__(self, other: "DicePackage") -> bool:
        return sum([dice == list(other.__iter__())[i] for i, dice in enumerate(self.__iter__())]) > 0
    
    def __ne__(self, other: "DicePackage") -> bool:
        return sum([dice != list(other.__iter__())[i] for i, dice in enumerate(self.__iter__())]) > 0
    
    def __post_init__(self):
        self.scale = Nonahedron() if self.scale is None else self.scale
        self.mobility = Nonahedron() if self.mobility is None else self.mobility
        self.morale = Nonahedron() if self.morale is None else self.morale
        
        self.roll()
    
    def roll(self):
        for mem in self.__iter__():
            mem.roll()

@dataclass
class BattleField:
    """
    1. 두 세력 집단에 대해 3d9를 실행한다. 각 주사위는 각각 "규모", "기동", "사기"를 결정한다.
    2. 9면체 주사위값에는 등급이 있는데 1부터 3은 최하등급으로 '처참함'이고, 4에서 6은 '무난함', 7과 8은 '성공', 9는 최고등급으로 '멋지게 성공'이다.
    3. 전투 주사위 경쟁(=전투 인카운터)은 분야 별 등급 대결로, 승리한 분야의 가짓수가 높은 쪽이 승리한다.
    
    충격 : 사기가 7 이상일 시 사용 가능, 사기를 소모해 같은 값의 기동 증대.
    화공 : 기동이 7 이상일 시 사용 가능, 기동을 소모해 같은 값의 규모 증대.
    맹공 : 기동이 7 이상일 시 사용 가능, 기동을 소모해 같은 값의 사기 증대.
    방비 : 규모가 7 이상일 시 사용 가능, 규모를 소모해 같은 값의 사기 증대.
    포위 : 규모가 7 이상일 시 사용 가능, 규모를 소모해 같은 값의 기동 증대.
    후퇴 : 해당 전투를 포기합니다.
    """
    
    active_f: Faction # 공격하는 세력 (전투 명령어를 실행한 측의 세력)
    passive_f: Faction # 공격당하는 세력 (실행된 명령어의 대상이 된 세력)
    
    def __post_init__(self):
        self.a_dice_pkg = DicePackage()
        self.p_dice_pkg = DicePackage()
        
    def get_flee_probablity(self, flee_dice: Nonahedron) -> float:
        """
        패배한 쪽은 도주 주사위(1d9)를 굴리고 병력의 생환율을 결정한다. 병력의 생환율은 다음과 같다.

        `{35 + (도주_주사위_값 * 5)}% /*소수점 내림*/`

        생환율의 최소치는 40%, 최대치는 85%다.
        """
        if flee_dice.last_roll is None: raise ValueError("도주 주사위의 값이 None입니다.")
        return (35 + (flee_dice.last_roll * 5)) / 100
    
    @property
    def winner(self):
        """
        승리한 세력을 반환한다.
        """
        if self.a_dice_pkg > self.p_dice_pkg:
            return self.active_f
        elif self.a_dice_pkg < self.p_dice_pkg:
            return self.passive_f
        else:
            return None
    
    @property
    def strategy_availablity_map(self) -> dict[Strategy, bool]:
        rtn = {
            Strategy.PASS: True,
            Strategy.SHOCK: self.a_dice_pkg.morale.last_roll >= 7,
            Strategy.FIREPOWER: self.a_dice_pkg.mobility.last_roll >= 7,
            Strategy.FIERCENESS: self.a_dice_pkg.mobility.last_roll >= 7,
            Strategy.DEFENSE: self.a_dice_pkg.scale.last_roll >= 7,
            Strategy.ENCIRCLEMENT: self.a_dice_pkg.scale.last_roll >= 7,
            Strategy.RETREAT: True
        }
        return rtn
    
    @property
    def strategy_function_map(self):
        return {
            Strategy.PASS: self.execute_strategy_retreat,
            Strategy.SHOCK: self.execute_strategy_shock,
            Strategy.FIREPOWER: self.execute_strategy_firepower,
            Strategy.FIERCENESS: self.execute_strategy_fierceness,
            Strategy.DEFENSE: self.execute_strategy_defense,
            Strategy.ENCIRCLEMENT: self.execute_strategy_encirclement,
            Strategy.RETREAT: self.execute_strategy_retreat
        }
        
    def get_battle_report_as_field(self):
        """
        전투 결과의 상세 정보를 discord embed에 사용될 수 있는 문자열로 반환한다.
        """
        rtn_list = [
            {
                "name": f"{self.active_f.name}",
                "value": str(self.a_dice_pkg)
            },
            {
                "name": f"{self.passive_f.name}",
                "value": str(self.p_dice_pkg)
            }
        ]
        return rtn_list
    
    def get_winner_as_field(self):
        """
        승리한 세력을 discord embed에 사용될 수 있는 문자열로 반환한다.
        """
        return {
            "name": "승리 세력",
            "value": self.winner.name if self.winner is not None else "무승부"
        }
        
    def is_strategy_available(self, strategy: Strategy) -> bool:
        
        return self.strategy_availablity_map[strategy]

    def execute_strategy_shock(self, amount: int):
        """
        전략: 충격
        """
        self.a_dice_pkg.mobility.last_roll += amount
        self.a_dice_pkg.morale.last_roll -= amount
        
    def execute_strategy_firepower(self, amount: int):
        """
        전략: 화공
        """
        self.a_dice_pkg.scale.last_roll += amount
        self.a_dice_pkg.mobility.last_roll -= amount
        
    def execute_strategy_fierceness(self, amount: int):
        """
        전략: 맹공
        """
        self.a_dice_pkg.morale.last_roll += amount
        self.a_dice_pkg.mobility.last_roll -= amount
        
    def execute_strategy_defense(self, amount: int):
        """
        전략: 방비
        """
        self.a_dice_pkg.morale.last_roll += amount
        self.a_dice_pkg.scale.last_roll -= amount
        
    def execute_strategy_encirclement(self, amount: int):
        """
        전략: 포위
        """
        self.a_dice_pkg.mobility.last_roll += amount
        self.a_dice_pkg.scale.last_roll -= amount
    
    def execute_strategy_retreat(self, amount: int):
        """
        전략: 후퇴
        """
        pass