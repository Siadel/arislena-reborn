"""
ExtInt라는 Int를 상속한 새로운 자료형 만들기
선언할 때 value, max_value, min_value를 지정해야 함
max_value와 min_value는 None으로 지정 가능
이 자료형은 연산으로 인해 max_value와 min_value를 넘어가는 경우, max_value와 min_value로 값을 고정시킴
모든 연산에서 반환하는 자료형은 자기 자신이어야 함
"""

class ExtInt(int):
    def __new__(cls, value: int, *, min_value: int = None, max_value: int = None):
        obj = super().__new__(cls, value)
        obj.__setattr__("max_value", max_value)
        obj.__setattr__("min_value", min_value)
        return obj
    
    def adjust_limitations(self, result: int):
        if self.max_value is not None:
            result = min(result, self.max_value)
        if self.min_value is not None:
            result = max(result, self.min_value)
        return self.__class__(result, self.max_value, self.min_value)

    def __add__(self, other):
        result = super().__add__(other)
        return self.adjust_limitations(result)

    def __sub__(self, other):
        result = super().__sub__(other)
        return self.adjust_limitations(result)

    def __mul__(self, other):
        result = super().__mul__(other)
        return self.adjust_limitations(result)

    def __truediv__(self, other):
        result = super().__truediv__(other)
        return self.adjust_limitations(result)
    
    def __floordiv__(self, other):
        result = super().__floordiv__(other)
        return self.adjust_limitations(result)

    def __mod__(self, other):
        result = super().__mod__(other)
        return self.adjust_limitations(result)

    def __pow__(self, other):
        return self.adjust_limitations(super().__pow__(other))

    def __str__(self):
        return "%d" % int(self)
    
    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({super().__repr__()}, max_value={self.max_value}, min_value={self.min_value})"

"""
ExtInt 오류 테스트
최소치가 0, 최대치가 100인 변수 a를 만들고, 10을 넣음
최소치가 0, 최대치가 100인 변수 b를 만들고, 100을 넣음
1. c에 a와 b를 더한 결과를 넣음
2. a와 b를 더한 결과와 c를 출력
3. c에 a와 b를 뺀 결과를 넣음
4. a와 b를 뺀 결과와 c를 출력
"""
if __name__ == "__main__":
    a = ExtInt(10, max_value=100, min_value=0)
    b = ExtInt(100, max_value=100, min_value=0)
    c = a + b
    print(a + b, c)
    print(type(a), type(b), type(c))
    c = a - b
    print(a - b, c)
    print(isinstance(a, int), isinstance(b, int), isinstance(c, int))