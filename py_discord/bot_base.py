import discord, logging, json, os, shutil, datetime, asyncio
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from copy import deepcopy
from threading import Thread
from pathlib import Path

from py_base import ari_enum
from py_base.ari_logger import ari_logger
from py_base.dbmanager import DatabaseManager
from py_base.ari_enum import ScheduleState
from py_base.utility import get_date, DATE_EXPR, BACKUP_DIR, FULL_DATE_EXPR_2
from py_base.jsonobj import BotSetting
from py_system.tableobj import Chalkboard, Deployment, Building, Resource, Crew, Livestock, CommandCounter, Laborable, JobSetting, GuildSetting
from py_system.tableobj import form_database_from_tableobjects
from py_system.systemobj import SystemBuilding
from py_discord import warnings

# 봇 권한 설정
intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.members = True

def exit_bot():
    ari_logger.critical("봇을 종료합니다.")
    exit(1)

class BotBase(commands.Bot):

    def __init__(
        self,
        bot_setting: BotSetting
    ):

        super().__init__(
            command_prefix="/",
            intents=intents,
            application_id=bot_setting.application_id
        )
        
        self.bot_setting = bot_setting
        self.main_guild: discord.Guild = discord.Object(id=bot_setting.main_guild_id)
        self.test_guild: discord.Guild = discord.Object(id=bot_setting.test_guild_id)
        self.guild_list: list[discord.Guild] = [discord.Object(id=guild_id) for guild_id in bot_setting.whitelist]
        
        self._token = self._get_token_or_exit(os.environ.get("ARISLENA_BOT_TOKEN"))
        self._log_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
        
        self._guild_server_manager: dict[str, "ServerManager"] = {}
    
    def get_database(self, guild_id: int | str) -> DatabaseManager:
        """
        usage example:
        ```
        bot.get_database(interaction.guild_id)
        ```
        """
        return self._guild_server_manager[str(guild_id)].database
    
    def get_server_manager(self, guild_id: int | str) -> "ServerManager":
        """
        usage example:
        ```
        bot.get_server_manager(interaction.guild_id)
        ```
        """
        return self._guild_server_manager[str(guild_id)]
        
    def _add_server_manager(self, guild_id: int | str):
        """
        길드 id별로 데이터베이스를 추가함.
        
        데이터베이스는 최종적으로 ./data/{guild_id}.db 위치에 생성됨
        """
        if isinstance(guild_id, int): guild_id = str(guild_id)
        db = DatabaseManager(guild_id)
        form_database_from_tableobjects(db)
        self._guild_server_manager[guild_id] = ServerManager(self, deepcopy(self.bot_setting), db, guild_id)
    
    def _get_token_or_exit(self, environ_get_result: str | None) -> str:
        """
        환경 변수에 ARISLENA_BOT_TOKEN이 없을 경우, json/token.json 파일을 확인하고 토큰을 반환함.
        """
        if environ_get_result is None: 
            
            token_return: str = None
            ari_logger.critical("환경 변수에 ARISLENA_BOT_TOKEN이 없습니다. json/token.json 파일을 확인합니다.")
            
            if not os.path.exists("json/token.json"):
                ari_logger.critical("json/token.json 파일이 없습니다.")
                exit_bot()
            
            with open("json/token.json", "r", encoding="utf-8") as f:
                if (token_return := json.load(f).get("ARISLENA_BOT_TOKEN")) is None:
                    ari_logger.critical("json/token.json 파일에 ARISLENA_BOT_TOKEN이 없습니다.")
                    exit_bot()
                    
            return token_return
        
        else: return environ_get_result
    
    async def announce_channel(self, message:str, channel_id:int):
        """
        지정된 채널에 메세지를 보냄.
        """
        if (channel := self.get_channel(channel_id)) is None: raise ValueError("채널을 찾을 수 없습니다.")
        await channel.send(message)
    
    async def announce_channel_with_embed(self, embed:discord.Embed, channel_id:int):
        """
        지정된 채널에 embed를 보냄.
        """
        if (channel := self.get_channel(channel_id)) is None: raise ValueError("채널을 찾을 수 없습니다.")
        await channel.send(embed=embed)

    def run(self):
        super().run(self._token, log_handler=self._log_handler, log_level=logging.INFO)

    def check_admin_or_raise(self, interaction: discord.Interaction):
        """
        서버에서 봇에게 정한 관리자 역할을 가지고 있는지 확인하는 함수
        
        관리자 역할이 없으면 warnings.NotAdmin 예외 발생
        """
        if not self.check_admin(interaction):
            raise warnings.NotAdmin()
        
    def check_admin(self, interaction: discord.Interaction) -> bool:
        """
        서버에서 봇에게 정한 관리자 역할을 가지고 있는지 확인하는 함수
        
        관리자 역할이 없으면 False 반환
        """
        if discord.utils.get(
            interaction.user.roles,
            id=self.get_server_manager(interaction.guild_id).guild_setting.admin_role_id
        ) is None:
            return False
        return True
    
    def check_user_or_raise(self, interaction: discord.Interaction):
        """
        서버에서 봇에게 정한 유저 역할을 가지고 있는지 확인하는 함수
        
        유저 역할이 없으면 warnings.NotUser 예외 발생
        """
        if discord.utils.get(
            interaction.user.roles,
            id=self.get_server_manager(interaction.guild_id).guild_setting.user_role_id
        ):
            return True
        return False
    
    def check_user_exists_or_raise(self, interaction: discord.Interaction):
        """
        아리슬레나에 등록되어 있지 않으면 warnings.NotRegistered 예외 발생
        """
        if not self.check_user_exists(interaction):
            raise warnings.NotRegistered(interaction.user.name)
        
    def check_user_not_exists_or_raise(self, interaction: discord.Interaction):
        """
        아리슬레나에 등록되어 있으면 warnings.AlreadyRegistered 예외 발생
        """
        if self.check_user_exists(interaction):
            raise warnings.AlreadyRegistered(interaction.user.name)
        
    def check_user_exists(self, interaction: discord.Interaction) -> bool:
        """
        아리슬레나에 등록되어 있는지 확인하는 함수
        """
        if self.get_database(interaction.guild_id).is_exist("user", discord_id=interaction.user.id) is None:
            return False
        return True

class ServerManager:
    
    def __init__(self, bot:BotBase, bot_setting:BotSetting, database:DatabaseManager, guild_id: int):
        """
        main_db: 게임의 메인 데이터베이스\n
        schedule: 스케줄 json 데이터\n
        """
        self.bot = bot
        self.bot_setting = bot_setting
        self.database = database
        self.guild_id = guild_id

        self.job_setting = JobSetting.from_database(self.database)
        self.guild_setting = GuildSetting.from_database(self.database)
        self.chalkboard = Chalkboard.from_database(self.database)
        self.chalkboard.state = ScheduleState.ONGOING

        # 스케줄러 생성
        self.event_loop = asyncio.new_event_loop()
        self.scheduler = AsyncIOScheduler(timezone='Asia/Seoul', event_loop=self.event_loop)
        self.scheduler_add_job()
        self.event_loop.create_task(self.scheduler_run())
        
        self.execute_thread = Thread(target=self.run_loop_forever)
        self.execute_thread.start()
        
        ari_logger.info(f"길드 {guild_id}의 스케줄러가 생성되었습니다.")
        
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
                ari_logger.info(f"길드 {self.guild_id}의 게임 시작 요청(이미 게임 시작됨)")
                return "게임이 이미 시작되었습니다. | 현재 턴: " + str(self.chalkboard.now_turn)
            
            case ScheduleState.WAITING:
                # 시작 대기 중일 때 (0)
                self.scheduler_add_job()
                self.chalkboard.push()
                
                ari_logger.info(f"길드 {self.guild_id}의 게임 시작 요청({(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPR)} 게임 시작 예정)")
                return f'게임 시작 대기 중 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPR)} 시작 예정'
            
            case ScheduleState.PAUSED:
                # 중단 중일 때 (2)
                self.scheduler.resume_job(self.form_schedule_id())
                
                self.chalkboard.state = ScheduleState.ONGOING
                self.chalkboard.push()

                ari_logger.info(f"길드 {self.guild_id}의 게임 재개 요청")
                return f'{get_date()} 게임 재개 되었습니다.'
            
            case ScheduleState.ENDED:
                return "종료된 게임은 재개할 수 없습니다."
            
    async def end_turn(self):
        '''
        게임 진행 함수(매일 21시 실행)
        '''
        
        ari_logger.info(f"길드 {self.guild_id}의 {self.chalkboard.now_turn}턴 종료 및 {self.chalkboard.now_turn+1}턴 시작 진행")
        
        await self.bot.announce_channel(
            f"# {self.chalkboard.now_turn}턴 종료 및 {self.chalkboard.now_turn+1}턴 시작 진행 보고",
            self.guild_setting.announce_channel_id
        )

        # 진행 상황 백업
        shutil.copy(self.database.file_path, BACKUP_DIR / Path(f"{get_date(FULL_DATE_EXPR_2)}_" + str(self.database.file_path.name)))

        if self.chalkboard.state == ScheduleState.WAITING:
            self.chalkboard.state = ScheduleState.ONGOING

        if self.chalkboard.now_turn >= self.chalkboard.turn_limit:
            self.end_game()
            return
        
        await self.execute_before_turn_end()
        
        ari_logger.info(f"길드 {self.guild_id}의 {self.chalkboard.now_turn}턴 종료")

        self.chalkboard.now_turn += 1
        
        await self.execute_after_turn_end()
        
        ari_logger.info(f"길드 {self.guild_id}의 {self.chalkboard.now_turn}턴 시작")
                
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

        ari_logger.info(f"길드 {self.guild_id}의 게임 중단 요청 | 현재 {self.chalkboard.now_turn}턴")
        
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

        ari_logger.info(f"길드 {self.guild_id}의 게임 종료 요청 | 현재 {self.chalkboard.now_turn}턴")
        
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
            await self.bot.announce_channel_with_embed(embed, self.guild_setting.announce_channel_id)
    
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
        
        await self.bot.announce_channel("\n".join(report_lines), self.guild_setting.announce_channel_id)
