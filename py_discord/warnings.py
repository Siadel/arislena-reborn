"""
봇이 출력할 경고 모음집
"""
from py_base import utility, koreanstring

class Default(Exception):
    def __init__(self, message: str):
        """
        Default은 AriBot에서 발생하는 모든 경고를 상속받는 클래스입니다.
        """
        super().__init__(message)

class NotRegistered(Default):
    def __init__(self, user_name:str=None):
        txt = "등록되지 않았어요! `/유저 등록` 명령어로 등록해주세요."
        if user_name:
            txt = f"{koreanstring.topicmarker(user_name, wrapper='**')} 등록되지 않았어요!"
        super().__init__(txt)

class AlreadyRegistered(Default):
    def __init__(self):
        super().__init__("이미 등록되어 있어요!")

class GamingNow(Default):
    def __init__(self):
        super().__init__("게임이 진행중이에요! 게임이 중단된 이후 다시 시도해주세요.")

class NotGamingNow(Default):
    def __init__(self):
        super().__init__("게임이 진행중이 아니에요! 게임이 시작된 이후 다시 시도해주세요.")

class NotAdmin(Default):
    def __init__(self):
        super().__init__("관리자 권한이 있는 유저만 사용할 수 있어요!")

class NotOwner(Default):
    def __init__(self):
        super().__init__("주인 권한이 있는 유저만 사용할 수 있어요!")

class NoFaction(Default):
    def __init__(self):
        super().__init__("세력을 아직 창설하지 않았어요!")

class NoBlock(Default):
    def __init__(self, category:str=None):
        if category is None:
            super().__init__("입력하신 조건에 맞는 블럭이 없어요!")
        else:
            super().__init__(f"안전한 상태인 '{category}' 블럭이 없어요!")

class NoTroop(Default):
    # 존재해서는 안 되는 에러지만 일단 구현은 해두기
    def __init__(self):
        super().__init__("입력하신 조건에 맞는 부대가 없어요!")

class NoDiplomacy(Default):
    def __init__(self):
        super().__init__("입력하신 조건에 맞는 외교 관계가 없어요!")

class NoBlockOwn(Default):
    def __init__(self, nation_name:str):
        super().__init__(f"나라 '{nation_name}'의 블록이 없어요! `/개척` 명령어로 블록을 만들어주세요.")

class NoRequiredBlock(Default):
    def __init__(self, category:str):
        super().__init__(f"'{category}' 블록이 없어요!")

class NoDiplomacyAct(Default):
    def __init__(self, category:str):
        super().__init__(f"'{category}' 외교 행동은 없어요!")

class NotLocated(Default):
    def __init__(self):
        super().__init__("목표한 블럭에 부대가 없어요!")

class MustOver0(Default):
    def __init__(self, mode:str|None, *args):
        """
        mode: and, or
        args: 1개 이상의 str, 명칭이어야 함
        """
        # args가 1개일 때
        if len(args) == 1:
            super().__init__(f"{koreanstring.topicmarker(args[0])} 0 이상이어야 해요!")
        # args가 여러 개일 때
        else:
            if mode == "and":
                super().__init__(f"{', '.join(args[:-1])}, {koreanstring.topicmarker(args[-1])} 모두 0 이상이어야 해요!")
            elif mode == "or":
                super().__init__(f"{', '.join(args)} 중 적어도 하나는 0 이상이어야 해요!")

class Shortage(Default):
    def __init__(self, item:str, amount:int, *, required:int|None=None):
        """
        item: str, 부족한 것의 명칭
        amount: int, 현재 가지고 있는 양
        required: int|None, 필요한 양
        """
        message = f"{koreanstring.nominative(item)} 부족해요.. 지금은 **{amount}**만큼 있어요."
        if required:
            message += f" 필요량은 **{required}**이에요!"
        super().__init__(message)

class ShortageMany(Default):
    def __init__(self, **kwargs):
        """
        kwargs: item(str):amount(int)
        """
        super().__init__(f"{utility.ENTER.join([f'{koreanstring.nominative(item)} 부족해요.. 지금은 **{amount}**만큼 있어요!' for item, amount in kwargs.items()])}")

class ShortageButNoInfo(Default):
    def __init__(self, item:str):
        super().__init__(f"{koreanstring.nominative(item)} 부족하다는 보고가 들어왔어요..")

class ShortageManyButNoInfo(Default):
    def __init__(self, *args):
        """
        args: item(str)
        """
        super().__init__(f"{utility.ENTER.join([f'{koreanstring.nominative(item)} 부족하다는 보고가 들어왔어요..' for item in args])}")

class TooMany(Default):
    def __init__(self, item:str, predict:int, limit:int, context:str|None=None):
        """
        item: 명칭
        predict: 예상량
        limit: 한계량
        context: 문맥 (ex. "상대국(의)")
        """
        if context:
            message = f"{context}의 {koreanstring.nominative(item)} 넘쳐요..! **({predict}/{limit})**"
        else:
            message = f"{koreanstring.nominative(item)} 넘쳐요..! **({predict}/{limit})**"
        super().__init__(message)

class AlreadyExist(Default):
    def __init__(self, item:str):
        super().__init__(f"{koreanstring.nominative(item)} 이미 있어요!")

class ExcessBlockCapacity(Default):
    def __init__(self, nation_name:str):
        super().__init__(f"'{nation_name}'의 블록 개수가 최대치에요!")

class InvalidItem(Default):
    def __init__(self, order:str):
        wrapper = "'"
        super().__init__(f"{koreanstring.topicmarker(order, wrapper=wrapper)} 존재하지 않아요!")

class InvalidCommand(Default):
    def __init__(self, argument_name:str=None):
        if argument_name:
            super().__init__(f"**{argument_name}** 인자에 입력하신 것이 맞지 않아요! 명령어 설명을 확인해주세요.")
        super().__init__("잘못된 명령어에요! 명령어 설명을 확인해주세요.")

class Impossible(Default):
    def __init__(self, additional:str|None=None):
        message = "불가능해요!"
        if additional:
            message += f" {additional}"
        super().__init__(message)

class TimeOut(Default):
    def __init__(self):
        super().__init__("시간이 초과되었습니다. 다시 시도해주세요.")

class MustPassThroughWallFirst(Default):
    def __init__(self):
        super().__init__("방어벽이 있는 나라는 방어벽으로밖에 이동할 수 없어요!")

class AlreadyDeployed(Default):
    def __init__(self, *, block_name:str=None, troop_name:str=None):
        """
        block_name, troop_name 둘 중 하나에는 무조건 값이 들어가야 함
        """
        if not block_name and not troop_name:
            raise ValueError("block_name, troop_name 둘 중 하나에는 무조건 값이 들어가야 함")
        if block_name:
            super().__init__(f"'{block_name}'에 부대가 이미 배치되어 있어요!")
        elif troop_name:
            super().__init__(f"'{troop_name}' 부대가 이미 배치되어 있어요!")

class NotDeployed(Default):
    def __init__(self, troop_name:str):
        super().__init__(f"'{troop_name}' 부대가 배치되어 있지 않아요!")

class MustExistLeastOne(Default):
    def __init__(self, context:str|None=None):
        if context:
            super().__init__(f"{koreanstring.topicmarker(context)} 적어도 하나 있어야 해요!")
        else:
            super().__init__("적어도 하나는 있어야 해요!")

class AlreadyAttacked(Default):
    def __init__(self):
        super().__init__("그 부대는 이 턴에 이미 공격했어요!")

class Least1(Default):
    def __init__(self):
        super().__init__("항목 중 하나는 적어도 1 이상이어야 해요!")

class NotSameNation(Default):
    def __init__(self):
        super().__init__("부대가 같은 나라에 있지 않아요!")

class InvalidChar(Default):
    def __init__(self, char:str):
        super().__init__(f"맨 끝의 {char} 문자는 사용할 수 없는 문자에요!")

class Duplicate(Default):
    def __init__(self, item:str, context:str=""):
        if len(context) > 0: context += " "
        super().__init__(f"{context}{koreanstring.nominative(item)} 중복됩니다!")

class NotAnyRole(Default):
    def __init__(self, *role_names):
        roles = ", ".join(role_names)
        super().__init__(f"이 명령어에는 {roles} 중 한 역할이 필요해요!")

class SubCommandNotFound(Default):
    def __init__(self, subcommand_name:str, choices:list[str]):
        super().__init__(f"{koreanstring.objective(subcommand_name)} 잘못 입력하셨습니다. {choices} 중 하나를 입력해주세요.")

class NotDomestic(Default):
    def __init__(self):
        super().__init__("자신이 세운 나라 안에 있는 부대를 대상으로만 가능해요!")

class Exceed(Default):
    def __init__(self, subject:str, limit:int, predict:int):
        super().__init__(f"{koreanstring.nominative(subject)} 한계를 초과했어요! 예상치: {predict}/{limit}")

class Deficient(Default):
    def __init__(self, subject:str, limit:int, predict:int):
        super().__init__(f"{koreanstring.nominative(subject)} 부족해요! 예상치: {predict}/{limit}")

class NameTooLong(Default):
    def __init__(self, subject:str, limit:int):
        super().__init__(f"{koreanstring.nominative(subject)} 이름이 너무 깁니다! 최대 길이: {limit}")

class NameContainsSpecialCharacter(Default):
    def __init__(self):
        super().__init__(f"이름에 특수문자가 포함되어 있습니다!")