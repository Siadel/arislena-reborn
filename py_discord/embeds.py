from discord import Embed, Colour

from py_base.ari_enum import ResourceCategory, WorkCategory
from py_base.dbmanager import DatabaseManager
from py_base.yamlobj import TableObjTranslator
from py_system.abstract import TableObject
from py_system.tableobj import Facility
from py_system.tableobj import User, Deployment, WorkerDescription
from py_system.systemobj import GeneralResource
from py_system.worker import Crew

def embed_for_user(*messages) -> Embed:
    """
    유저 DM으로 보낼 embed 생성
    """

    embed = Embed(title="안녕하세요! 아리슬레나의 아리입니다.", color=Colour.blue())

    for message in messages:
        embed.add_field(name="", value=message, inline=False)
    
    return embed

def parse_embeds(title:str, fields:list[dict], quantity:int=25) -> list[Embed]:
    """
    embed를 여러 개 만들어서 반환합니다.
    ---
    title: embed의 제목
    
    quantity: 한 embed에 들어갈 field의 수 (기본값: 25)
    
    args' component = {
        "name" : ...,
        "value" : ...,
        "inline" : True / False
    }
    """
    embeds = []
    embed = Embed(title=title, color=Colour.blue())
    for field in fields:
        embed.add_field(**field)
        if len(embed.fields) == quantity:
            embeds.append(embed)
            embed = Embed(title=title, color=Colour.blue())
    embeds.append(embed)
    return embeds

# /유저 등록
def register(user:User):
    """
    유저 등록
    """
    embed = Embed(title="환영합니다!", description="다음 정보가 저장되었습니다.", color=Colour.green())
    embed.add_field(name="디스코드 아이디", value=user.discord_id)
    embed.add_field(name="유저네임", value=user.discord_name)
    embed.add_field(name="등록일", value=user.register_date)
    return embed

def add_resource_insufficient_field(embed: Embed, consume_resource_category:ResourceCategory) -> Embed:
    embed.add_field(
        name=f"자원 부족: {consume_resource_category.express()}",
        value="자원이 부족하여 생산을 진행할 수 없습니다."
    )
    return embed

class ArislenaEmbed(Embed):
    
    def __init__(self, title: str, description: str = None, colour: Colour = Colour.blue()):
        super().__init__(title=title, description=description, colour=colour)

class TableObjectEmbed(ArislenaEmbed):
    
    def __init__(self, title: str, description: str = None):
        super().__init__(title, description, Colour.green())
    
    def add_basic_info(self, table_obj: TableObject, translate: TableObjTranslator):
        """
        TableObject의 기본 정보를 embed에 추가합니다.
        """
        self.add_field(name="기본 정보", value=table_obj.to_embed_value(translate))
        return self
    

class ResourceConsumeEmbed(ArislenaEmbed):
    
    def __init__(self, title: str, description: str, crew_list: list[Crew], consume_resource_list: list[GeneralResource]):
        super().__init__(title, description, Colour.yellow())
        self.crew_list = crew_list
    
    def add_resource_insufficient_field(self):
        pass
    

class CrewLookupEmbed(ArislenaEmbed):
    
    def __init__(self, crew: Crew, database: DatabaseManager, translator: TableObjTranslator):
        super().__init__(title="대원 정보", colour=Colour.green())
        self.crew = crew
        self.database = database
        self.translator = translator
        
    def add_basic_field(self):
        self.add_field(name="기본 정보", value=self.crew.to_embed_value(self.translator))
        return self
    
    def add_location_field(self):
        if (d_data := self.database.fetch(
            Deployment.table_name, worker_id = self.crew.id
        )):
            d_obj = Deployment.from_data(d_data)
            b_obj = Facility.from_database(self.database, id=d_obj.facility_id)
            self.add_field(
                name="위치 정보",
                value=f"{b_obj.name} ({b_obj.category.express()})"
            )
        else:
            self.add_field(
                name="위치 정보",
                value="배치되지 않음"
            )
        return self
    
    # def add_labor_detail_field(self):
    #     self.add_field(
    #         name="컨디션",
    #         value=WorkerDetail.get_from_corresponding(
    #             Nonahedron().set_last_roll(self.crew.labor).last_judge
    #         ).get_detail(
    #             self.crew.labor_detail_index
    #         )
    #     )
    #     return self
    
    def add_description_field(self):
        self.add_field(
            name="상태와 특징",
            value=WorkerDescription.from_database(self.database, worker_id = self.crew.id).to_embed_value(self.translator)
            
        )
        return self
    
    def add_experience_field(self):
        value_text_list = []
        for category in WorkCategory.to_list():
            exp = self.crew.get_experience(category)
            value_text_list.append(
                exp.to_embed_value()
            )
        self.add_field(
            name="경험치 현황",
            value="\n".join(value_text_list)
        )
        return self