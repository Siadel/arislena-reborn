from py_base.ari_enum import ResourceCategory
from py_base.arislena_dice import Dice
from py_system.abstract import HasCategoryAndAmount


class GeneralResource(HasCategoryAndAmount):

    def __init__(
        self,
        category: ResourceCategory,
        amount: int = 1
    ):
        super().__init__(category, amount)


class Spades(GeneralResource):
    def __init__(self, amount:int = 1):
        super().__init__(ResourceCategory.SPADES, amount)

class Diamonds(GeneralResource):
    def __init__(self, amount:int = 1):
        super().__init__(ResourceCategory.DIAMONDS, amount)
        
class Hearts(GeneralResource):
    def __init__(self, amount:int = 1):
        super().__init__(ResourceCategory.HEARTS, amount)

class Clubs(GeneralResource):
    def __init__(self, amount:int = 1):
        super().__init__(ResourceCategory.CLUBS, amount)
        
class Gold(GeneralResource):
    def __init__(self, amount:int = 1):
        super().__init__(ResourceCategory.GOLD, amount)


class ProductionResource(HasCategoryAndAmount):

    def __init__(
        self,
        category: ResourceCategory,
        amount: int = 1,
        dice_ratio: int = 1
    ):
        super().__init__(category, amount)
        self.dice_ratio = dice_ratio # 1 이상의 정수

    def __str__(self) -> str:
        return f"{self.category.name}; 주사위 값 {self.dice_ratio} 당 {self.amount}개 생산"

    def _return_general_resource(self, dice: int) -> GeneralResource:
        # dice_ratio 당 amount를 계산한다.
        # dice_ratio가 1이면 amount가 그대로 반환된다.
        # dice_ratio가 2이면 amount가 절반이 된다.

        return GeneralResource(self.category, self.amount * (dice // self.dice_ratio))

    def __mul__(self, other: int | Dice) -> GeneralResource:
        dice: int = 0
        if isinstance(other, int):
            dice = other
        elif isinstance(other, Dice):
            if other._last_roll is None: raise ValueError("주사위를 굴려주세요")
            dice = other._last_roll
        else:
            raise TypeError(f"int 또는 Dice 타입만 가능합니다. (현재 타입: {type(other)})")

        return self._return_general_resource(dice)



class SpadesProduction(ProductionResource):
    def __init__(self, amount:int = 1, dice_ratio:int = 1):
        super().__init__(ResourceCategory.SPADES, amount, dice_ratio)
        
class DiamondsProduction(ProductionResource):
    def __init__(self, amount:int = 1, dice_ratio:int = 1):
        super().__init__(ResourceCategory.DIAMONDS, amount, dice_ratio)
        
class HeartsProduction(ProductionResource):
    def __init__(self, amount:int = 1, dice_ratio:int = 1):
        super().__init__(ResourceCategory.HEARTS, amount, dice_ratio)

class ClubsProduction(ProductionResource):
    def __init__(self, amount:int = 1, dice_ratio:int = 1):
        super().__init__(ResourceCategory.CLUBS, amount, dice_ratio)
        
class GoldProduction(ProductionResource):
    def __init__(self, amount:int = 1, dice_ratio:int = 1):
        super().__init__(ResourceCategory.GOLD, amount, dice_ratio)