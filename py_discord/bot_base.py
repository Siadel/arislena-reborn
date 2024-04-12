import discord, logging, json, os, shutil, datetime, asyncio
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import Iterator
from copy import deepcopy
from threading import Thread

from py_base import utility
from py_base.dbmanager import DatabaseManager
from py_base import ari_enum
from py_base.ari_enum import ScheduleState
from py_base.utility import get_date, DATE_EXPRESSION, BACKUP_DIR, DATE_EXPRESSION_FULL_2, DATE_EXPRESSION_FULL
from py_base.jsonobj import GameSetting, JobSetting, BotSetting
from py_system._global import setting_by_guild, bot_setting
from py_system.tableobj import Chalkboard, Deployment, Building, Resource, Crew, Livestock, CommandCounter, Laborable, GameSetting, JobSetting
from py_system.tableobj import form_database_from_tableobjects
from py_system.systemobj import SystemBuilding


# 봇 권한 설정
intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.members = True

def exit_bot():
    print("봇을 종료합니다.")
    exit(1)

class BotBase(commands.Bot):

    def __init__(
        self,
        bot_setting: BotSetting
    ):

        super().__init__(
            command_prefix="/",
            intents=intents,
            application_id=bot_setting.application_id)
        
        self.bot_setting = bot_setting
        self.guild_list: list[discord.Guild] = [discord.Object(id=guild_id) for guild_id in bot_setting.guild_ids]
        
        self._token = self._get_token_or_exit(os.environ.get("ARISLENA_BOT_TOKEN"))
        self._log_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        
        self._guild_database: dict[str, DatabaseManager] = {}
        self._guild_schedule: dict[str, "ScheduleManager"] = {}

    @property
    def guild_database(self) -> dict[str, DatabaseManager]:
        return self._guild_database
    
    @property
    def guild_schedule(self) -> dict[str, "ScheduleManager"]:
        return self._guild_schedule
        
    def _add_database_and_scheduler(self, guild_id: int | str):
        """
        길드 id별로 데이터베이스를 추가함.
        
        데이터베이스는 최종적으로 ./data/{guild_id}.db 위치에 생성됨
        """
        if isinstance(guild_id, int): guild_id = str(guild_id)
        db = DatabaseManager(guild_id)
        form_database_from_tableobjects(db)
        self._guild_database[guild_id] = db
        self._guild_schedule[guild_id] = ScheduleManager(self, deepcopy(self.bot_setting), db, guild_id)
    
    def _get_token_or_exit(self, environ_get_result: str | None) -> str:
        """
        환경 변수에 ARISLENA_BOT_TOKEN이 없을 경우, json/token.json 파일을 확인하고 토큰을 반환함.
        """
        if environ_get_result is None: 
            
            token_return: str = None
            print("환경 변수에 ARISLENA_BOT_TOKEN이 없습니다. json/token.json 파일을 확인합니다.")
            
            if not os.path.exists("json/token.json"):
                print("json/token.json 파일이 없습니다.")
                exit_bot()
            
            with open("json/token.json", "r", encoding="utf-8") as f:
                if (token_return := json.load(f).get("ARISLENA_BOT_TOKEN")) is None:
                    print("json/token.json 파일에 ARISLENA_BOT_TOKEN이 없습니다.")
                    exit_bot()
                    
            return token_return
        
        else: return environ_get_result

    async def announce(self, message:str, guild_id:int):
        """
        지정된 봇 전용 공지 채널에 메세지를 보냄. 지정 채널이 없으면 아무것도 하지 않음.
        """
        if (guild_id_key := str(guild_id)) in setting_by_guild.announce_location:
            
            channel = self.get_channel(setting_by_guild.announce_location[guild_id_key])
            await channel.send(message)
            
    async def announce_with_embed(self, embed:discord.Embed, guild_id:int):
        """
        지정된 봇 전용 공지 채널에 embed를 보냄. 지정 채널이 없으면 아무것도 하지 않음.
        """
        if (guild_id_key := str(guild_id)) in setting_by_guild.announce_location:
            
            channel = self.get_channel(setting_by_guild.announce_location[guild_id_key])
            await channel.send(embed=embed)

    def run(self):
        super().run(self._token, log_handler=self._log_handler, log_level=logging.INFO)


class ScheduleManager:
    
    def __init__(self, bot:BotBase, bot_setting:BotSetting, database:DatabaseManager, guild_id: int):
        """
        main_db: 게임의 메인 데이터베이스\n
        schedule: 스케줄 json 데이터\n
        """
        self.bot = bot
        self.bot_setting = bot_setting
        self.database = database
        self.guild_id = guild_id
        
        self.game_setting = GameSetting.from_database(self.database)
        self.job_setting = JobSetting.from_database(self.database)
        self.chalkboard = Chalkboard.from_database(self.database)
        self.chalkboard.state = ScheduleState.ONGOING

        # 스케줄러 생성
        self.event_loop = asyncio.new_event_loop()
        self.scheduler = AsyncIOScheduler(timezone='Asia/Seoul', event_loop=self.event_loop)
        self.scheduler_add_job()
        self.event_loop.create_task(self.scheduler_run())
        
        self.execute_thread = Thread(target=self.run_loop_forever)
        self.execute_thread.start()
        
        print(f"길드 {guild_id}의 스케줄러가 생성되었습니다.")
        
    def form_schedule_id(self) -> str:
        return f"arislena-{self.guild_id}"

    def __del__(self):
        self.scheduler.shutdown()

    def scheduler_add_job(self):
        self.scheduler.add_job(
            self.end_turn, 
            **self.job_setting.get_dict_without_id(),
            id=self.form_schedule_id()
        )
    
    async def scheduler_run(self):
        asyncio.set_event_loop(self.event_loop)
        self.scheduler.start()
        
    def run_loop_forever(self):
        self.event_loop.run_forever()
    
    def start_game(self):
        '''
        게임 시작 함수
        ---------------
        - 이미 게임 진행 중이면 return
        - 게임 중단 중이면 재개
        - 게임 중 아니면 schedule.json 생성
        '''
        
        match self.chalkboard.state:
            
            case ScheduleState.ONGOING:
                
                print(f'{get_date()} 게임 시작 요청(이미 게임 시작됨)')
                return "게임이 이미 시작되었습니다. | 현재 턴: " + str(self.chalkboard.now_turn)
            
            case ScheduleState.WAITING:
                # 시작 대기 중일 때 (0)
                self.scheduler_add_job()
                self.chalkboard.push()
                
                print(f'{get_date()} 게임 시작 요청 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)} 게임 시작 예정')
                return f'게임 시작 대기 중 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)} 시작 예정'
            
            case ScheduleState.PAUSED:
                # 중단 중일 때 (2)
                self.scheduler.resume_job(self.form_schedule_id())
                
                self.chalkboard.state = ScheduleState.ONGOING
                self.chalkboard.push()
                
                message = f'{get_date()} 게임 재개 되었습니다.'
                print(message)
                return message
            
            case ScheduleState.ENDED:
                return "종료된 게임은 재개할 수 없습니다."
            
    async def end_turn(self):
        '''
        게임 진행 함수(매일 21시 실행)
        '''
        
        print(f"{get_date(DATE_EXPRESSION_FULL)}\t{self.chalkboard.now_turn}턴 진행")
        
        await self.bot.announce(
            f"# {self.chalkboard.now_turn}턴 종료 및 {self.chalkboard.now_turn+1}턴 시작 진행 보고",
            self.guild_id
        )

        # 진행 상황 백업
        shutil.copy(self.database.file_path, BACKUP_DIR + f"{get_date(DATE_EXPRESSION_FULL_2)}_"+self.database.file_path)

        if self.chalkboard.state == ScheduleState.WAITING:
            self.chalkboard.state = ScheduleState.ONGOING

        if self.chalkboard.now_turn >= self.game_setting.turn_limit:
            self.end_game()
            return
        
        await self.execute_before_turn_end()
        
        print(f"{get_date(DATE_EXPRESSION_FULL)}\t{self.chalkboard.now_turn}턴 종료")

        self.chalkboard.now_turn += 1
        
        await self.execute_after_turn_end()
        
        print(f"{get_date(DATE_EXPRESSION_FULL)}\t{self.chalkboard.now_turn}턴 시작")
                
        self.chalkboard.push()
        
        self.database.connection.commit()

    def stop_game(self):
        '''
        게임 중단 함수
        '''

        if self.chalkboard.state != ScheduleState.WAITING and self.chalkboard.state != ScheduleState.ONGOING:
            return "게임이 진행 중이 아닙니다."
        
        self.chalkboard.state = ScheduleState.PAUSED
        self.chalkboard.push()

        self.scheduler.pause_job(self.form_schedule_id())

        print(f"게임 중단 됨 | 현재 {self.chalkboard.now_turn}턴")
        
        self.database.connection.commit()
        return f"게임이 중단 되었습니다. | 현재 {self.chalkboard.now_turn}턴"

    def end_game(self):
        '''
        게임 종료 함수
        '''
        
        self.chalkboard.state = ScheduleState.ENDED
        self.chalkboard.end_date = get_date()

        self.scheduler.remove_job(self.form_schedule_id())

        self.chalkboard.push()

        print("게임 종료 됨")
        
        self.database.connection.commit()
        # 게임 종료 메시지 추가 예정
        return "게임이 종료 되었습니다."
    
    def building_produce(self) -> list[discord.Embed]:
        # 모든 건물이 생산을 실행
        # TODO 코드 작성
        
        result_embed_list = []
        
        # 배치 현황에서 unique한 건물 아이디별로 전체 row 불러오기
        for building_id_row in self.database.cursor.execute(f"SELECT DISTINCT building_id FROM {Deployment.__name__}")\
                .fetchall():
            building_id = building_id_row[0]
            deployment_row_list = self.database.fetch_many(Deployment.__name__, building_id=building_id)
            deployment_list = [Deployment.from_data(row) for row in deployment_row_list]
            # 건물과 대원, 가축 불러오기
            building = Building.from_database(self.database, id=building_id)
            deployed_crews = building.get_deployed_crews(deployment_list)
            deployed_livestocks = building.get_deployed_livestocks(deployment_list)
            
            sys_building = SystemBuilding.get_sys_building_from_building(building)
            production_recipe = sys_building.get_production_recipe()
            
            result_embed = discord.Embed(
                title = f"**{building.name}**({building.category.express()}) 생산 결과",
                colour = discord.Colour.yellow()
            )
            
            # 건물에 배치된 노동원마다 실행
            for labor in deployed_crews + deployed_livestocks:
                # 자원 소모
                resource_insufficient = False
                embed_value_list = [f"- 배치 노동원: {labor.name}", f"- 노동력: {labor.labor}"]
                for consume_resource in production_recipe.consume:
                    
                    r_data = self.database.fetch(Resource.__name__, faction_id=building.faction_id, category=consume_resource.category)
                    
                    if r_data is None:
                        embed_value_list.append("자원이 부족해 생산을 진행할 수 없습니다.")
                        result_embed.add_field(
                            name=f"자원 부족: {consume_resource.category.express()}",
                            value="\n".join(embed_value_list)
                        )
                        resource_insufficient = True
                        continue
                    
                    r = Resource.from_database(self.database, faction_id=building.faction_id, category=consume_resource.category)
                    
                    if r < consume_resource:
                        embed_value_list.append("자원이 부족해 생산을 진행할 수 없습니다.")
                        result_embed.add_field(
                            name=f"자원 부족: {consume_resource.category.express()}",
                            value="\n".join(embed_value_list)
                        )
                        resource_insufficient = True
                    else:
                        r.amount -= consume_resource.amount
                        embed_value_list.append(f"- 소모량: {consume_resource.amount}")
                        result_embed.add_field(
                            name=f"{consume_resource.category.express()}",
                            value="\n".join(embed_value_list)
                        )
                        r.push()
                
                if resource_insufficient: continue
                
                # 자원 생산
                for produce_resource in production_recipe.produce:
                    
                    r_data = self.database.fetch(Resource.__name__, faction_id=building.faction_id, category=produce_resource.category)
                    r: Resource
                    if r_data is None:
                        r = Resource(
                            faction_id=building.faction_id,
                            category=produce_resource.category,
                        )
                        r.set_database(self.database)
                    else:
                        r = Resource.from_database(self.database, faction_id=building.faction_id, category=produce_resource.category)
                    
                    produced_resource = produce_resource * labor.labor
                    r.amount += produced_resource.amount
                    
                    result_embed.add_field(
                        name=f"{produce_resource.category.express()}",
                        value=f"- 배치 노동원: {labor.name}\n- 노동력: {labor.labor}\n- 생산량: **{produced_resource.amount}**"
                    )
                    
                    r.push()
        
            result_embed_list.append(result_embed)
                
        return result_embed_list
    
    def crew_consume(self) -> list[discord.Embed]:
        pass

    async def execute_before_turn_end(self):
        '''
        턴 종료 시 실행 함수
        '''
        building_produce_embed_list = self.building_produce()
        for embed in building_produce_embed_list:
            await self.bot.announce_with_embed(embed, self.guild_id)
    
    async def execute_after_turn_end(self):
        '''
        턴 시작 시 실행 함수
        '''
        
        report_lines = []
        
        # availablity가 STANDBY인 모든 Crew, Livestock을 IDLE로 변경하고, labor를 설정함
        laborable_tables:list[Crew | Livestock] = Laborable.__subclasses__()
        for table in laborable_tables:
            for row in self.database.fetch_many(table.__name__, availability=ari_enum.Availability.UNAVAILABLE.value):
                obj = table.from_data(row)
                obj.set_database(self.database)
                obj.availability = ari_enum.Availability.STANDBY
                
                obj.push()
        
        self.database.connection.commit()
        
        report_lines.append(
            f"- **{ari_enum.Availability.UNAVAILABLE.express()}** 상태인 모든 대원과 가축이 **{ari_enum.Availability.STANDBY.express()}** 상태로 변경되었습니다."
        )
        
        for table in laborable_tables:
            for row in self.database.fetch_many(table.__name__, availability=ari_enum.Availability.STANDBY.value):
                obj = table.from_data(row)
                obj.set_database(self.database)
                obj.set_labor_dice()
                obj.labor = obj.labor_dice * obj.labor_time
                
                obj.push()
        
        report_lines.append(
            f"- **{ari_enum.Availability.STANDBY.express()}** 상태인 모든 대원과 가축의 노동력이 설정되었습니다."
        )

        # 모든 CommandCounter 0으로 설정
        cc_list = [CommandCounter.from_data(cc) for cc in self.database.fetch_all(CommandCounter.__name__)]
        for cc in cc_list:
            cc.set_database(self.database)
            cc.reset()
            cc.push()
            
        report_lines.append(
            f"- 모든 명령 카운터가 초기화 되었습니다."
        )
        
        await self.bot.announce("\n".join(report_lines), self.guild_id)
