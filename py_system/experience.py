from py_base.ari_enum import ExperienceCategory
from py_system.abstract import ExperienceAbst

OPTIMIZED_MIN_EXP_BY_LEVEL = (
    0, 12, 36, 72, 120, 180, 252, 336, 432, 540, 660, 792, 936, 1092
)

def level_to_min_experience(level: int) -> int:
    """
    레벨을 그 레벨을 달성하기 위한 최소 경험치로 변환함
    """
    return (3 / 2) * ((2 * level + 1)**2 - 1)

class GeneralExperience(ExperienceAbst):

    def __init__(
        self,
        category: ExperienceCategory,
        amount: int = 1
    ):
        super().__init__(category, amount)
        
class Hunting(ExperienceAbst):

    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.HUNTING, amount)
        
class Gathering(ExperienceAbst):

    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.GATHERING, amount)
        
class Argiculture(ExperienceAbst):

    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.AGRICULTURE, amount)
        
class Pasturing(ExperienceAbst):

    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.PASTURING, amount)
        
class Combat(ExperienceAbst):
    
    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.COMBAT, amount)

class Strategy(ExperienceAbst):
    
    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.STRATEGY, amount)

class Administration(ExperienceAbst):
        
    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.ADMINISTRATION, amount)
        
class Construction(ExperienceAbst):
    
    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.CONSTRUCTION, amount)
        
class Manufacturing(ExperienceAbst):
    
    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.MANUFACTURING, amount)
        
class Pharmacy(ExperienceAbst):
    
    def __init__(
        self,
        amount: int = 1
    ):
        super().__init__(ExperienceCategory.PHARMACY, amount)