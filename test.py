
from dataclasses import dataclass
from typing import ClassVar

# @dataclass(slots=True)
# class Foo:
#     mutual: ClassVar[int] = 100
#     id: int
#     name: str
#     amount: int
#     ratio: float

#     def some_method(self):
#         # self.some_instance_var = 100
#         pass

# @dataclass(slots=True)
# class SubFoo(Foo):
#     id: int
#     name: str
#     amount: int
#     ratio: float
#     additional: str
    
#     @property
#     def slots(self):
#         return list(super(Foo).__slots__) + list(self.__slots__)

# if __name__ == "__main__":
#     foo = Foo(1, 'foo', 100, 0.5)
#     subfoo = SubFoo(1, 'foo', 100, 0.5, "some_text")

#     print(foo.__slots__, subfoo.__slots__, subfoo.slots)
    # assert subfoo.__slots__ == ('id', 'name', 'amount', 'ratio', 'additional') # assertion error. why?

# @dataclass
# class Bar:
#     mutual: ClassVar[int] = 100
#     id: int
#     name: str
#     amount: int
#     ratio: float
    
#     def __len__(self):
#         return len(self.get_dict())
    
#     @property
#     def bar(self):
#         return self._bar
    
#     @bar.setter
#     def bar(self, value):
#         self._bar = value
    
#     @property
#     def some_property(self):
#         return self.id * self.amount
    
#     def get_dict(self) -> dict:
#         """
#         self.__dict__를 호출하나 key가 '_'로 시작하는 것은 제외
#         """
#         return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

# if __name__ == "__main__":
#     # bar = Bar(1, 'bar', 100, 0.5)
#     # print(bar.get_dict())
#     # bar.bar = 100
#     # print(bar.get_dict())
#     # print(Bar.__annotations__)
#     # print(len(bar))
#     print({"id", "name"}.issubset(Bar.__annotations__.keys()))

from abc import ABCMeta

class BuilderPattern(metaclass=ABCMeta):
    
    def __init__(self):
        self._builded = False
    
    def build(self):
        self._builded = True
        return self

class Fooable(metaclass=ABCMeta):
    
    def set_foo(self, param):
        self.foo = param
        return self

class Barable(metaclass=ABCMeta):
    
    def set_bar(self, param):
        self.bar = param
        return self
        
class FooBar(Fooable, Barable, BuilderPattern):
    
    def __init__(self, original_param):
        BuilderPattern.__init__(self)
        self.original_param = original_param
        self.foo = None
        self.bar = None
        
if __name__ == "__main__":
    fb = FooBar("Any object")
    
    print(fb.foo, fb.bar)