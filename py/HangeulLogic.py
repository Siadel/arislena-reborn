"""
한글의 한국어적 분석을 하는 모듈
- 음절의 초성, 중성, 종성을 분리하고 분석 가능함
- 해당 음절이 한글인지 아닌지도 파악 가능
"""
def is_hangeul(c) -> bool:
    return 0xAC00 <= ord(c) <= 0xD7A3

def idx_to_codepoint(onset_idx:int, nucleus_idx:int, coda_idx:int) -> int:
    """
    Jamo에 있는 초성, 중성, 종성의 인덱스를 받아 유니코드 코드 포인트를 반환한다.
    """
    return 0xAC00 + (onset_idx * 21 + nucleus_idx) * 28 + coda_idx

def idx_to_syllable(onset_idx:int, nucleus_idx:int, coda_idx:int) -> str:
    """
    Jamo에 있는 초성, 중성, 종성의 인덱스를 받아 음절을 반환한다.
    """
    return chr(idx_to_codepoint(onset_idx, nucleus_idx, coda_idx))


class Base:
    def __init__(self):
        self.character:str|None = None

    def __str__(self) -> str|None:
        return self.character

class Jamo(Base):
    """
    이 객체는 한글 자모에 대한 클래스다.
    초성, 중성, 종성에 대한 순서를 가지고 있다.
    """

    loc = ("onset", "nucleus", "coda")
    
    # "": 비어 있음
    # None: 자모가 아님
    onset = ("ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ", None)
    nucleus = ("ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", 
        "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ", None)
    coda = ("", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ",
        "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ",
        "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ", None)

    jamoset = set(onset + nucleus + coda)

    # "가"의 유니코드 값은 AC00이다.
    # "힣"의 유니코드 값은 D7A3이다.
    # 한글의 유니코드 값은 0xAC00 + (초성 * 21 + 중성) * 28 + 종성이다.
    # 이를 이용해 음절에서 자모 역계산이 가능하다.

    @classmethod
    def split(cls, ord_syllable:int):
        # 한글 음절의 코드값을 받아 초성, 중성, 종성을 반환한다.

        ord_syllable -= 0xAC00
        coda = ord_syllable % 28
        nucleus = (ord_syllable // 28) % 21
        onset = (ord_syllable // 28) // 21

        return cls(Jamo.onset[onset], "onset"), cls(Jamo.nucleus[nucleus], "nucleus"), cls(Jamo.coda[coda], "coda")

    def __init__(self, jamo:str|None=None, location:str|None=None, *, idx:int=-1):
        # 한글 자모와 위치를 받아, 몇 번째 자모인지 저장한다.
        super().__init__()
        self.character = jamo
        self.location = location if jamo else None
        self.idx:int = idx
        if self.character and self.location:
            self.idx = getattr(Jamo, self.location).index(jamo)

    def __add__(self, other:str):
        if isinstance(other, str):
            if self.location == "onset" and other in self.nucleus:
                return Syllable(onset=self, nucleus=Jamo(other, "nucleus"))

class Syllable(Base):
    """
    한국어 음절을 나타내는 클래스
    """

    csf = ("한글", "공백", "숫자", "영문", "특수문자", "기타")

    @classmethod
    def classify(cls, character:str) -> str:
        # 글자를 한글, 공백, 숫자, 영문, 기타로 분류한다.
        if is_hangeul(character):
            return cls.csf[0]
        elif character == " ":
            return cls.csf[1]
        elif character.isdigit():
            return cls.csf[2]
        elif character.isalpha():
            return cls.csf[3]
        else:
            return cls.csf[-1]

    def __init__(self, syllable:str|None=None, *, 
        onset:Jamo=Jamo(), nucleus:Jamo=Jamo(), coda:Jamo=Jamo()):
        # 한글 음절은 초성, 중성, 종성으로 나뉜다.
        # 이 객체는 len이 1인 한글 음절을 받아 초성, 중성, 종성을 분리한다.
        # 초성(onset), 중성(nucleus), 종성(coda)은 한글 자모에 해당한다.
        super().__init__()
        self.character:str|None = syllable
        self.codepoint:int = ord(syllable) if syllable else 0
        self.onset:Jamo = onset
        self.nucleus:Jamo = nucleus
        self.coda:Jamo = coda
        self.ingredients = [self.onset, self.nucleus, self.coda]

        if self.character:
            self.classification = self.classify(self.character)
            if self.classification == "한글":
                self.onset, self.nucleus, self.coda = Jamo.split(self.codepoint)
                
        else:
            # 적어도 초성과 종성 모두의 character가 None이 아니어야 한다.
            if not self.onset.character or not self.nucleus.character:
                raise ValueError("적어도 초성과 중성이 인자로 들어와야 합니다.")
            self.character = idx_to_syllable(self.onset.idx, self.nucleus.idx, self.coda.idx)

    def has_coda(self):
        if self.classification == "한글":
            return self.coda.character != ""
        elif self.classification == "영문":
            if self.character in ["n", "m", "l"]:
                return True
            return False
        elif self.classification == "숫자":
            if self.character in ["0", "1", "3", "6", "7", "8"]:
                return True
            return False
        else:
            raise ValueError("한글, 영문, 숫자만 가능합니다.")

    def rhyme(self):
        # nucleus와 coda를 tuple로 합쳐서 반환한다.

        return (self.nucleus, self.coda)

    def add_coda(self, coda):
        # 종성을 추가한다.

        self.coda = Jamo(coda, "coda")
        self.character = idx_to_syllable(self.onset.idx, self.nucleus.idx, self.coda.idx)

    def __add__(self, ja:str):
        # add_coda와 논리는 같지만, Syllable 객체를 반환한다.
        # 종성이 ""인 경우에만 가능
        # 종성을 붙인 새로운 Syllable 객체를 반환한다.
        # 붙이는 자는 무조건 coda로 간주한다.
        if self.coda.character != "":
            raise ValueError("coda is not empty")
        jamo = Jamo(ja, "coda")

        return Syllable(onset=self.onset, nucleus=self.nucleus, coda=jamo)
            

def test1():
    test = "뎅커와 만민어군은 10월에 Stelo의 새 스태프로 데뷔했다."
    print("원문: " + test)
    for t in test:
        syl = Syllable(t)
        print(syl.character, syl.classification, syl.onset.character, syl.nucleus.character, syl.coda.character)

def test2():
    sylsumtest = Syllable("미") + "ㅇ"
    for i in sylsumtest.ingredients:
        print(i.character, i.location, i.idx)


# 테스트 코드

if __name__ == "__main__":
    test1()