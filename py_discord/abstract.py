import discord
from discord.ui import Button
from abc import ABCMeta, abstractmethod
from typing import Type, Any
from copy import deepcopy


from py_base.dbmanager import DatabaseManager
from py_base.yamlobj import TableObjTranslator
from py_system.tableobj import TableObject
from py_discord import warnings, embeds
from py_discord.bot_base import BotBase


# view 전용 추상 클래스
class BuilderPattern(metaclass=ABCMeta):
    
    def __init__(self):
        self._builded = False
    
    def build(self):
        self._builded = True
        return self

    @staticmethod
    def require_builded(func):
        """
        클래스가 build() 메소드를 실행한 상태에서만 실행되도록 하는 데코레이터
        
        build() 메소드를 실행하지 않은 상태에서 실행하면 ValueError를 발생시킴
        """
        def wrapper(self: "BuilderPattern", *args, **kwargs):
            if not self._builded: raise ValueError("빌드되지 않은 객체입니다.")
            return func(self, *args, **kwargs)
        return wrapper


class TableObjectButton(Button, BuilderPattern, metaclass=ABCMeta):
    
    corr_obj_type:Type[TableObject] = TableObject
    
    def __init__(self, bot: BotBase, interaction_for_this:discord.Interaction):
        """
        사용법:
        ```python3
        btn = TableObjectButton(...).set_table_object(table_object)
        ```
        """
        Button.__init__(self, style = discord.ButtonStyle.primary)
        BuilderPattern.__init__(self)
        
        self._table_object: TableObject = None
        self._bot: BotBase = bot
        self._database: DatabaseManager = bot.get_database(interaction_for_this.guild_id)
        self._interaction_for_this: discord.Interaction = interaction_for_this
        
        self.label_complementary: str = None
        
    @abstractmethod
    def clone(self):
        """
        build하기 이전, 버튼의 속성을 복사한 새로운 버튼 객체를 반환
        """
        return deepcopy(self)
    
    def _get_basic_embed(self):
        return embeds.TableObjectEmbed(f"{self.label} 정보").add_basic_info(
                self._table_object,
                TableObjTranslator()
            )
    
    def _check_type(self, object: Any):
        if type(object) != self.__class__.corr_obj_type:
            raise TypeError(f"{object.__class__} 클래스는 {self.__class__.corr_obj_type} 클래스의 객체와 호환되지 않습니다.")
    
    def check_interruption(self, interaction:discord.Interaction):
        """
        view의 버튼이 다른 유저에 의해 눌렸을 때 발생하는 오류를 방지합니다.
        """
        if interaction.user.id != self._interaction_for_this.user.id: raise warnings.ImpossibleToInterrupt()
    
    def _set_label_complementary(self, table_object:TableObject):
        pass
        
    def set_table_object(self, table_object:TableObject):
        self._check_type(table_object)
        self._set_label_complementary(table_object)
        
        self._table_object = table_object
        return self
    
    def build(self):
        BuilderPattern.build(self)
        label_txt = self._table_object.get_display_string()

        if self.label_complementary: label_txt += f" ({self.label_complementary})"
        # <메인으로 출력할 데이터> (<서브로 보여줄 데이터 컬럼 한국어명> : <서브로 출력할 데이터>) 형태
        self.label = label_txt
        return self
    
    def disable_or_not(self):
        """
        이 버튼을 view에 추가하기 전에 버튼을 비활성화할지 여부를 결정합니다.
        
        이 버튼에 해당하는 객체에 대해 버튼이 정의한 행동이 불가능한 경우에 버튼을 비활성화합니다.
        """
        pass
    
    async def callback(self, interaction:discord.Interaction):
        await interaction.response.send_message(
            embed = self._get_basic_embed(),
            ephemeral = False # 일단은 False로
        )