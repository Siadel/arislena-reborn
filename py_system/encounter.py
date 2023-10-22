from abc import ABCMeta, abstractmethod

class Encounter(metaclass=ABCMeta):

    def __init__(self, initiator, target):
        pass

    @abstractmethod
    def execute(self):
        pass