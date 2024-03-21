from pprint import pprint

from py_base.ari_enum import Strategy
from py_system.battlefield import BattleField, DicePackage
from py_system.tableobj import Faction

evoker = Faction(name="Evoker")

bf = BattleField(
    evoker,
    Faction(name="Blue Team")
)

pprint(bf.get_battle_report_as_field())

print(bf.strategy_availablity_map)

while strategy := Strategy(int(input("전략 번호를 입력하세요(0부터, 속행/충격/화공/맹공/방비/포위/후퇴, 6까지): "))) != Strategy.PASS:
    
    if not bf.is_strategy_available(strategy):
        print("전략을 사용할 수 없습니다.")
        print(bf.strategy_availablity_map)
        continue

    amount = int(input("전략의 수치를 입력하세요: "))
    bf.strategy_function_map[strategy](amount)
    
    

pprint(bf.get_winner_as_field())

if evoker == bf.winner:
    print("승리! 상대의 생환율을 계산합니다.")
    print(f"상대의 생환율: {bf.get_flee_probablity()}")
elif bf.winner is None:
    print("무승부")
else:
    print("패배! 도주 주사위를 굴립니다.")
    print(f"아군 생환율: {bf.get_flee_probablity()}")