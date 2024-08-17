from py_base import ari_enum, name_generator
from py_base.arislena_dice import D20
from py_system.abstract import GeneralResource, WorkerQualification
from py_system.tableobj import WorkerDescription, WorkerExperience, Worker

import random
from math import sqrt

class Crew(Worker):

    correspond_category = ari_enum.WorkerCategory.CREW
    qualification = WorkerQualification(ari_enum.WorkCategory.get_everything_but_unset())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def new(cls, faction_id: int):
        """
        faction_id에 해당하는 세력에 새로운 대원을 생성함

        대원의 이름은 "대원 {random_number}"로 설정됨
        """
        # random_number = str(random.random()).split(".")[1]
        bs = ari_enum.BiologicalSex.get_random()
        new_crew = cls(
            faction_id=faction_id, 
            name=name_generator.get_random_full_name(bs.value), 
            category=cls.correspond_category, 
            bio_sex=bs
        )
        new_crew.set_efficiency()
        return new_crew

    def get_experience_level(self, worker_exp: WorkerExperience) -> int:
        return int((-1 + sqrt(1 + 2/3 * worker_exp.experience)) // 2)

    def get_consumption_recipe(self) -> list[GeneralResource]:
        return [
            GeneralResource(ari_enum.ResourceCategory.FOOD, 1),
            GeneralResource(ari_enum.ResourceCategory.WATER, 1)
        ]

    def get_description(self) -> WorkerDescription:
        self._check_database()
        desc = WorkerDescription.from_data(self._database.fetch(WorkerDescription.table_name, worker_id=self.id))
        if desc.worker_id != self.id: desc.worker_id = self.id
        return desc

    def get_every_experience(self) -> list[WorkerExperience]:
        return [self.get_experience(category) for category in ari_enum.WorkCategory.get_everything_but_unset()]


class Livestock(Worker):

    correspond_category = ari_enum.WorkerCategory.LIVESTOCK
    qualification = WorkerQualification([ari_enum.WorkCategory.AGRICULTURE])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def new(cls, faction_id: int):
        """
        faction_id에 해당하는 세력에 새로운 가축을 생성함

        가축의 이름은 "가축 {random_number}"로 설정됨
        """
        random_number = str(random.random()).split(".")[1]
        new_livestock = cls(faction_id=faction_id, name=f"가축 {random_number}", category=cls.correspond_category, sex=ari_enum.BiologicalSex.get_random())
        return new_livestock

    def get_experience_level(self, worker_exp: WorkerExperience) -> int:
        # exp 150 당 레벨 1 증가, 3까지만 증가 가능
        return min(3, int(worker_exp.experience // 150))

    def get_consumption_recipe(self) -> list[GeneralResource]:
        return [
            GeneralResource(ari_enum.ResourceCategory.FEED, 1),
            GeneralResource(ari_enum.ResourceCategory.WATER, 2)
        ]

    def get_display_string(self) -> str:
        if self.name:
            return self.name
        return f"가축 {self.id}"


# class Crew(Worker):
#     
#     correspond_category = WorkerCategory.CREW

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

#     def get_experience_level(self, worker_exp: WorkerExperience) -> int:
#         return int((-1 + sqrt(1 + 2/3 * worker_exp.experience)) // 2)

#     @classmethod
#     def new(cls, faction_id: int):
#         """
#         faction_id에 해당하는 세력에 새로운 대원을 생성함

#         대원의 이름은 "대원 {random_number}"로 설정됨
#         """
#         # random_number = str(random.random()).split(".")[1]
#         bs = BiologicalSex.get_random()
#         new_crew = cls(faction_id=faction_id, name=name_generator.get_random_full_name(bs.value), category=cls.correspond_category, sex=bs)
#         new_crew.set_labor()
#         return new_crew

#     def get_consumption_recipe(self) -> list[GeneralResource]:
#         return [
#             GeneralResource(ResourceCategory.FOOD, 1),
#             GeneralResource(ResourceCategory.WATER, 1)
#         ]

#     def get_description(self) -> WorkerDescription:
#         self._check_database()
#         desc = WorkerDescription.from_data(self._database.fetch(WorkerDescription.table_name, worker_id=self.id))
#         if desc.worker_id != self.id: desc.worker_id = self.id
#         return desc

#     def get_every_experience(self) -> list[WorkerExperience]:
#         return [self.get_experience(category) for category in WorkCategory.to_list()]

#     def set_efficiency_dice(self):

#         self._efficiency_dice = D20()
#         return self

#     def get_labor_by_WorkCategory(self, category: WorkCategory):
#         return self.labor + self.get_experience_level(self.get_experience(category))

#     def set_labor(self):
#         """
#         노동력 설정
#         """
#         if self._efficiency_dice is None: self.set_efficiency_dice()
#         self.labor = self._efficiency_dice.roll()
#         return self

#     def get_display_string(self) -> str:
#         return self.name

#     def is_available(self) -> bool:
#         return self.availability.is_available()


# class Livestock(Worker):
#     
#     correspond_category = WorkerCategory.LIVESTOCK

#     def __init__(self, **kwargs):
#         Worker.__init__(self, **kwargs)

#     @classmethod
#     def new(cls, faction_id: int):
#         """
#         faction_id에 해당하는 세력에 새로운 가축을 생성함

#         가축의 이름은 "가축 {random_number}"로 설정됨
#         """
#         random_number = str(random.random()).split(".")[1]
#         new_livestock = cls(faction_id=faction_id, name=f"가축 {random_number}", category=cls.correspond_category, sex=BiologicalSex.get_random())
#         return new_livestock

#     def get_experience_level(self, worker_exp: WorkerExperience) -> int:
#         # exp 150 당 레벨 1 증가, 3까지만 증가 가능
#         return min(3, int(worker_exp.experience // 150))

#     def get_consumption_recipe(self) -> list[GeneralResource]:
#         return [
#             GeneralResource(ResourceCategory.FEED, 1),
#             GeneralResource(ResourceCategory.WATER, 2)
#         ]

#     def get_display_string(self) -> str:
#         if self.name:
#             return self.name
#         return f"가축 {self.id}"

#     def set_efficiency_dice(self):
#         """
#         기본적으로 주사위 결과에 3을 더함 (최소 4)
#         """
#         self._efficiency_dice = D20(dice_mod=3)
#         return self

#     def set_labor(self):
#         if self._efficiency_dice is None: self.set_efficiency_dice()
#         self.labor = self._efficiency_dice.roll()
#         return self