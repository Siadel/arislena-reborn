
from dataclasses import dataclass

class wrapper:
    
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return str(self.value)

    def __int__(self):
        return int(self.value)

@dataclass
class Foo:
    a: wrapper
    b: wrapper

    def __post_init__(self):
        self.a = wrapper("aasdf", self.a)
        self.b = wrapper("b3erfgs", self.b)

foo = Foo(1, "2")
print(foo.a.name, foo.a)
print(foo.b.name, foo.b)
