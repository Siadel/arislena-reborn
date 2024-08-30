import discord, shutil, datetime, asyncio
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from threading import Thread
from pathlib import Path

from py_base import ari_enum, yamlobj
from py_base.ari_logger import ari_logger
from py_base.dbmanager import DatabaseManager
from py_base.ari_enum import ScheduleState
from py_base.utility import get_date, DATE_FORMAT, BACKUP_DIR, FULL_DATE_FORMAT_NO_SPACE
from py_base.jsonobj import BotSetting
from py_system.tableobj import Chalkboard, Deployment, CommandCounter, JobSetting, GuildSetting
from py_system.worker import Livestock

from py_discord import turn_progress
from py_system.worker import Crew

class ServerManager:
    
    def __init__(self, bot:commands.Bot, bot_setting:BotSetting, database:DatabaseManager, guild_id: int):
        """
        main_db: 게임의 메인 데이터베이스\n
        schedule: 스케줄 json 데이터\n
        """
        self.bot = bot
        self.bot_setting = bot_setting
        self.database = database
        self.guild_id = guild_id
        
        self.detail = yamlobj.Detail()
        self.table_obj_translator = yamlobj.TableObjTranslator()
        self.event_text = yamlobj.EventText()

        self.job_setting = JobSetting.from_database(self.database)
        self.guild_setting = GuildSetting.from_database(self.database)
        self.chalkboard = Chalkboard.from_database(self.database)
        self.chalkboard.schedule_state = ScheduleState.ONGOING
        
        self.announce_channel = self.bot.get_channel(self.guild_setting.announce_channel_id)

        # 스케줄러 생성
        self.event_loop = asyncio.new_event_loop()
        self.scheduler = AsyncIOScheduler(timezone='Asia/Seoul', event_loop=self.event_loop)
        self.scheduler_add_job()
        self.event_loop.create_task(self.scheduler_run())
        
        self.execute_thread = Thread(target=self.run_loop_forever)
        self.execute_thread.start()
        
        ari_logger.info(f"길드 {guild_id}의 스케줄러가 생성되었습니다.")

    def __del__(self):
        self.scheduler.shutdown()

    def form_schedule_id(self) -> str:
        return f"arislena-{self.guild_id}"

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
        
        match self.chalkboard.schedule_state:
            
            case ScheduleState.ONGOING:
                ari_logger.info(f"길드 {self.guild_id}의 게임 시작 요청(이미 게임 시작됨)")
                return "게임이 이미 시작되었습니다. | 현재 턴: " + str(self.chalkboard.now_turn)
            
            case ScheduleState.WAITING:
                # 시작 대기 중일 때 (0)
                self.scheduler_add_job()
                self.chalkboard.push()
                
                ari_logger.info(f"길드 {self.guild_id}의 게임 시작 요청({(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_FORMAT)} 게임 시작 예정)")
                return f'게임 시작 대기 중 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_FORMAT)} 시작 예정'
            
            case ScheduleState.PAUSED:
                # 중단 중일 때 (2)
                self.scheduler.resume_job(self.form_schedule_id())
                
                self.chalkboard.schedule_state = ScheduleState.ONGOING
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
        
        await self.announce_channel.send(
            content=f"# {self.chalkboard.now_turn}턴 종료 및 {self.chalkboard.now_turn+1}턴 시작 진행 보고"
        )

        # 진행 상황 백업
        shutil.copy(self.database.file_path, BACKUP_DIR / Path(f"{get_date(FULL_DATE_FORMAT_NO_SPACE)}_" + str(self.database.file_path.name)))

        if self.chalkboard.schedule_state == ScheduleState.WAITING:
            self.chalkboard.schedule_state = ScheduleState.ONGOING

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

        if self.chalkboard.schedule_state != ScheduleState.WAITING and self.chalkboard.schedule_state != ScheduleState.ONGOING:
            return "게임이 진행 중이 아닙니다."
        
        self.chalkboard.schedule_state = ScheduleState.PAUSED
        self.chalkboard.push()

        self.scheduler.pause_job(self.form_schedule_id())

        ari_logger.info(f"길드 {self.guild_id}의 게임 중단 요청 | 현재 {self.chalkboard.now_turn}턴")
        
        self.database.connection.commit()
        return f"게임이 중단 되었습니다. | 현재 {self.chalkboard.now_turn}턴"

    def end_game(self):
        '''
        게임 종료 함수
        '''
        
        self.chalkboard.schedule_state = ScheduleState.ENDED
        self.chalkboard.end_date = get_date()

        self.scheduler.remove_job(self.form_schedule_id())

        self.chalkboard.push()

        ari_logger.info(f"길드 {self.guild_id}의 게임 종료 요청 | 현재 {self.chalkboard.now_turn}턴")
        
        self.database.connection.commit()
        # 게임 종료 메시지 추가 예정
        return "게임이 종료 되었습니다."
    
    def crew_consume(self) -> list[discord.Embed]:
        pass

    async def execute_before_turn_end(self):
        '''
        턴 종료 시 실행 함수
        '''
        ari_logger.info(f"길드 {self.guild_id}의 {self.chalkboard.now_turn}턴 종료 진행")
        for facility_id in Deployment.get_unique_facility_ids(self.database):
            await self.announce_channel.send(embed=turn_progress.facility_progress(self.database, facility_id))
    
    async def execute_after_turn_end(self):
        '''
        턴 시작 시 실행 함수
        '''
        
        report_lines = []
        
        # availablity가 STANDBY인 모든 Crew, Livestock을 IDLE로 변경하고, labor를 설정함
        worker_types = [Crew, Livestock]
        for laborable_table in worker_types:
            laborable_table: Crew|Livestock
            for row in self.database.fetch_many(laborable_table.table_name, availability=ari_enum.Availability.UNAVAILABLE.value):
                obj = laborable_table.from_data(row)
                obj.set_database(self.database)
                obj.availability = ari_enum.Availability.STANDBY
                
                obj.push()
        
        self.database.connection.commit()
        
        report_lines.append(
            f"- **{ari_enum.Availability.UNAVAILABLE.express()}** 상태인 모든 대원과 가축이 **{ari_enum.Availability.STANDBY.express()}** 상태로 변경되었습니다."
        )
        for laborable_table in worker_types:
            for row in self.database.fetch_many(laborable_table.table_name, availability=ari_enum.Availability.STANDBY.value):
                obj = laborable_table.from_data(row)
                obj.set_database(self.database)\
                    .set_efficiency()
                
                # Crew의 경우 기본 노동력에 따른 efficiency_detail을 설정
                if isinstance(obj, Crew):
                    desc = obj.get_description()\
                        .set_database(self.database)\
                        .set_worker_efficiency_detail(obj.efficiency_dice.last_judge.name, self.detail)
                    desc.push()

                obj.push()
        
        report_lines.append(
            f"- **{ari_enum.Availability.STANDBY.express()}** 상태인 모든 대원과 가축의 노동력이 설정되었습니다."
        )

        # 모든 CommandCounter 0으로 설정
        cc_list = [CommandCounter.from_data(cc) for cc in self.database.fetch_all(CommandCounter.table_name)]
        for cc in cc_list:
            cc.set_database(self.database)
            cc.reset()
            cc.push()
            
        report_lines.append(
            f"- 모든 명령 카운터가 초기화 되었습니다."
        )
        
        await self.announce_channel.send(content="\n".join(report_lines))
