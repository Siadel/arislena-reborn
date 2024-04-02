
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

@dataclass
class Bar:
    mutual: ClassVar[int] = 100
    id: int
    name: str
    amount: int
    ratio: float
    
    @property
    def some_property(self):
        return self.id * self.amount

if __name__ == "__main__":
    bar = Bar(1, 'bar', 100, 0.5)
    print(bar.some_property, bar.__dict__)