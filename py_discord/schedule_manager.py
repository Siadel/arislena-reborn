from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import shutil, datetime, discord

from py_base import ari_enum
from py_base.ari_enum import ScheduleState
from py_base.utility import get_date, DATE_EXPRESSION, BACKUP_DIR, DATE_EXPRESSION_FULL_2, DATE_EXPRESSION_FULL
from py_base.dbmanager import MainDB
from py_base.jsonobj import Schedule, GameSetting, JobSetting, BotSetting
from py_base.arislena_dice import Nonahedron
from py_system import tableobj, systemobj
from py_discord.bot_base import BotBase
from py_discord.embeds import add_resource_insufficient_field

ARISLENA_JOB_ID = "game_schedule"

class ScheduleManager:
    
    def __init__(self, bot:BotBase, bot_setting:BotSetting, main_db:MainDB, schedule:Schedule, game_setting:GameSetting, job_setting:JobSetting):
        """
        main_db: 게임의 메인 데이터베이스\n
        schedule: 스케줄 json 데이터\n
        """
        self.bot = bot
        self.bot_setting = bot_setting
        self.main_db = main_db
        self.schedule = schedule
        self.game_setting = game_setting
        self.job_setting = job_setting

        self.scheduler = AsyncIOScheduler(timezone='Asia/Seoul')
        self.scheduler.start()
        self.sched_add_job()
        self.schedule.state = ScheduleState.ONGOING

    def __del__(self):
        self.scheduler.shutdown()

    def sched_add_job(self):
        self.scheduler.add_job(
            self.end_turn, 
            **self.job_setting.__dict__,
            id=ARISLENA_JOB_ID
        )
    
    def start_game(self):
        '''
        게임 시작 함수
        ---------------
        - 이미 게임 진행 중이면 return
        - 게임 중단 중이면 재개
        - 게임 중 아니면 schedule.json 생성
        '''
        
        match self.schedule.state:
            
            case ScheduleState.ONGOING:
                
                print(f'{get_date()} 게임 시작 요청(이미 게임 시작됨)')
                return "게임이 이미 시작되었습니다. | 현재 턴: " + str(self.schedule.now_turn)
            
            case ScheduleState.WAITING:
                # 시작 대기 중일 때 (0)
                self.sched_add_job()
                self.schedule.dump()
                
                print(f'{get_date()} 게임 시작 요청 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)} 게임 시작 예정')
                return f'게임 시작 대기 중 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)} 시작 예정'
            
            case ScheduleState.PAUSED:
                # 중단 중일 때 (2)
                self.scheduler.resume_job(ARISLENA_JOB_ID)
                
                self.schedule.state = ScheduleState.ONGOING
                self.schedule.dump()
                
                message = f'{get_date()} 게임 재개 되었습니다.'
                print(message)
                return message
            
            case ScheduleState.ENDED:
                return "종료된 게임은 재개할 수 없습니다."

        # if self.schedule.state == ScheduleState.ONGOING:
        #     print(f'{get_date()} 게임 시작 요청(이미 게임 시작됨)')
        #     return "게임이 이미 시작되었습니다. | 현재 턴: " + str(self.schedule.now_turn)
            
        # elif self.schedule.state == ScheduleState.WAITING:
        #     # 시작 대기 중일 때 (0)
        #     self.sched_add_job()
        #     self.schedule.dump()
            
        #     print(f'{get_date()} 게임 시작 요청 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)} 게임 시작 예정')
        #     return f'게임 시작 대기 중 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)} 시작 예정'
        
        # elif self.schedule.state == ScheduleState.PAUSED:
        #     # 중단 중일 때 (2)
        #     self.schedule.state = ScheduleState.ONGOING
        #     self.schedule.dump()

        #     self.scheduler.resume_job(ARISLENA_JOB_ID)
            
        #     message = f'{get_date()} 게임 재개 되었습니다.'
        #     print(message)
        #     return message

        # elif self.schedule.state == ScheduleState.ENDED:
        #     return "종료된 게임은 재개할 수 없습니다."
    
    async def end_turn(self):
        '''
        게임 진행 함수(매일 21시 실행)
        ------------------------------
        진행 턴수가 60 이상이면 sched 종료
        '''
        
        print(f"{get_date(DATE_EXPRESSION_FULL)}\t{self.schedule.now_turn}턴 진행")
        
        await self.bot.announce(
            f"# {self.schedule.now_turn}턴 종료 및 {self.schedule.now_turn+1}턴 시작 진행 보고",
            self.bot_setting.main_guild_id
        )

        # 진행 상황 백업
        shutil.copy(self.main_db.path, BACKUP_DIR + f"{get_date(DATE_EXPRESSION_FULL_2)}_"+self.main_db.filename)

        if self.schedule.state == ScheduleState.WAITING:
            self.schedule.state = ScheduleState.ONGOING

        if self.schedule.now_turn >= self.game_setting.arislena_end_turn:
            self.end_game()
            return
        
        await self.execute_before_turn_end()
        
        print(f"{get_date(DATE_EXPRESSION_FULL)}\t{self.schedule.now_turn}턴 종료")

        self.schedule.now_turn += 1
        
        await self.execute_after_turn_end()
        
        print(f"{get_date(DATE_EXPRESSION_FULL)}\t{self.schedule.now_turn}턴 시작")
                
        self.schedule.dump()

    def stop_game(self):
        '''
        게임 중단 함수
        '''

        if self.schedule.state != ScheduleState.WAITING and self.schedule.state != ScheduleState.ONGOING:
            return "게임이 진행 중이 아닙니다."
        
        self.schedule.state = ScheduleState.PAUSED
        self.schedule.dump()

        self.scheduler.pause_job(ARISLENA_JOB_ID)

        print(f"게임 중단 됨 | {self.schedule.now_turn}일 차")
        return f"게임이 중단 되었습니다. | {self.schedule.now_turn}일 차"

    def end_game(self):
        '''
        게임 종료 함수
        '''
        
        self.schedule.state = ScheduleState.ENDED
        self.schedule.end_date = get_date()

        self.scheduler.remove_job(ARISLENA_JOB_ID)

        self.schedule.dump()

        print("게임 종료 됨")
        # 게임 종료 메시지 추가 예정
        return "게임이 종료 되었습니다."
    
    def building_produce(self) -> list[discord.Embed]:
        # 모든 건물이 생산을 실행
        # TODO 코드 작성
        
        result_embed_list = []
        
        # 배치 현황에서 unique한 건물 아이디별로 전체 row 불러오기
        for building_id_row in self.main_db.cursor.execute(f"SELECT DISTINCT building_id FROM {tableobj.Deployment.__name__}")\
                .fetchall():
            building_id = building_id_row[0]
            deployment_row_list = self.main_db.fetch_many(tableobj.Deployment.__name__, building_id=building_id)
            deployment_list = [tableobj.Deployment.from_data(row) for row in deployment_row_list]
            # 건물과 대원, 가축 불러오기
            building = tableobj.Building.from_database(self.main_db, id=building_id)
            deployed_crews = building.get_deployed_crews(deployment_list)
            deployed_livestocks = building.get_deployed_livestocks(deployment_list)
            
            sys_building = systemobj.get_sys_building_from_building(building)
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
                    
                    r_data = self.main_db.fetch(tableobj.Resource.__name__, faction_id=building.faction_id, category=consume_resource.category)
                    
                    if r_data is None:
                        embed_value_list.append("자원이 부족해 생산을 진행할 수 없습니다.")
                        result_embed.add_field(
                            name=f"자원 부족: {consume_resource.category.express()}",
                            value="\n".join(embed_value_list)
                        )
                        resource_insufficient = True
                        continue
                    
                    r = tableobj.Resource.from_database(self.main_db, faction_id=building.faction_id, category=consume_resource.category)
                    
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
                    
                    r_data = self.main_db.fetch(tableobj.Resource.__name__, faction_id=building.faction_id, category=produce_resource.category)
                    r: tableobj.Resource
                    if r_data is None:
                        r = tableobj.Resource(
                            faction_id=building.faction_id,
                            category=produce_resource.category,
                        )
                        r.set_database(self.main_db)
                    else:
                        r = tableobj.Resource.from_database(self.main_db, faction_id=building.faction_id, category=produce_resource.category)
                    
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
            await self.bot.announce_with_embed(embed, self.bot_setting.main_guild_id)
        
        self.main_db.connection.commit()
    
    async def execute_after_turn_end(self):
        '''
        턴 시작 시 실행 함수
        '''
        
        report_lines = []
        
        # availablity가 STANDBY인 모든 Crew, Livestock을 IDLE로 변경하고, labor를 설정함
        laborable_tables:list[tableobj.Crew | tableobj.Livestock] = tableobj.Laborable.__subclasses__()
        for table in laborable_tables:
            for row in self.main_db.fetch_many(table.__name__, availability=ari_enum.Availability.UNAVAILABLE.value):
                obj = table.from_data(row)
                obj.set_database(self.main_db)
                obj.availability = ari_enum.Availability.STANDBY
                
                obj.push()
        
        self.main_db.connection.commit()
        
        report_lines.append(
            f"- **{ari_enum.Availability.UNAVAILABLE.express()}** 상태인 모든 대원과 가축이 **{ari_enum.Availability.STANDBY.express()}** 상태로 변경되었습니다."
        )
        
        for table in laborable_tables:
            for row in self.main_db.fetch_many(table.__name__, availability=ari_enum.Availability.STANDBY.value):
                obj = table.from_data(row)
                obj.set_database(self.main_db)
                obj.set_labor_dice()
                obj.labor = obj.labor_dice * obj.labor_time
                
                obj.push()
        
        report_lines.append(
            f"- **{ari_enum.Availability.STANDBY.express()}** 상태인 모든 대원과 가축의 노동력이 설정되었습니다."
        )

        # 모든 CommandCounter 0으로 설정
        cc_list = [tableobj.CommandCounter.from_data(cc) for cc in self.main_db.fetch_all(tableobj.CommandCounter.__name__)]
        for cc in cc_list:
            cc.set_database(self.main_db)
            cc.reset()
            cc.push()
            
        report_lines.append(
            f"- 모든 명령 카운터가 초기화 되었습니다."
        )
        
        await self.bot.announce("\n".join(report_lines), self.bot_setting.main_guild_id)

        self.main_db.connection.commit()
