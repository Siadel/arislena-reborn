from apscheduler.schedulers.background import BackgroundScheduler
import shutil, datetime

from py_base.ari_enum import ScheduleState
from py_base.utility import get_date, DATE_EXPRESSION, BACKUP_DIR, DATE_EXPRESSION_FULL_2, DATE_EXPRESSION_FULL
from py_base.dbmanager import DatabaseManager
from py_base.jsonobj import Schedule, GameSetting

ARISLENA_JOB_ID = "game_schedule"

class ScheduleManager:
    def __init__(self, main_db:DatabaseManager, schedule:Schedule, game_setting:GameSetting):
        """
        main_db: 게임의 메인 데이터베이스\n
        schedule: 스케줄 json 데이터\n
        """
        self.sched = BackgroundScheduler(timezone='Asia/Seoul')
        self.main_db = main_db
        self.schedule = schedule
        self.settings = game_setting

        self.sched.start()
        self.sched_add_job()
        self.schedule.state = ScheduleState.ONGOING

    def __del__(self):
        self.sched.shutdown()

    def sched_add_job(self):
        self.sched.add_job(
            self.ongoing_game, 
            "cron", 
            # day_of_week=self.settings.cron_days_of_week, 
            hour=self.settings.cron_hour, 
            minute="00", 
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

        if self.schedule.state == ScheduleState.ONGOING:
            print(f'{get_date()} 게임 시작 요청(이미 게임 시작됨)')
            return "게임이 이미 시작되었습니다. | 현재 턴: " + str(self.schedule.now_turn)
            
        else:
            if self.schedule.state == ScheduleState.WAITING:
                # 시작 대기 중일 때 (0)
                self.sched_add_job()
                self.schedule.dump()
                
                print(f'{get_date()} 게임 시작 요청 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)} 게임 시작 예정')
                return f'게임 시작 대기 중 | {(datetime.date.today() + datetime.timedelta(days=1)).strftime(DATE_EXPRESSION)} 시작 예정'
            
            elif self.schedule.state == ScheduleState.PAUSED:
                # 중단 중일 때 (2)
                self.schedule.state = ScheduleState.ONGOING
                self.schedule.dump()

                self.sched.resume_job(ARISLENA_JOB_ID)
                
                message = f'{get_date()} 게임 재개 되었습니다.'
                print(message)
                return message

            elif self.schedule.state == ScheduleState.ENDED:
                return "종료된 게임은 재개할 수 없습니다."
    
    def ongoing_game(self):
        '''
        게임 진행 함수(매일 자정 실행)
        ------------------------------
        진행 턴수가 60 이상이면 sched 종료
        '''

        # 진행 상황 백업
        shutil.copy(self.main_db.path, BACKUP_DIR + f"{get_date(DATE_EXPRESSION_FULL_2)}_"+self.main_db.filename)

        if self.schedule.state == ScheduleState.WAITING:
            self.schedule.state = ScheduleState.ONGOING

        if self.schedule.now_turn >= self.settings.arislena_end_turn:
            self.end_game()
            return

        self.schedule.now_turn += 1
        
        print(self.schedule.now_turn.__str__() + f'일차 시작 {get_date(DATE_EXPRESSION_FULL)}')

        # 나라의 블럭에 대한 업데이트 사항
        # 블럭이 없으면 continue
        # constants = jsonwork.load_json("constants.json")
        # for nation in self.main_db.fetch_all_nations():
        #     # 모든 유저 식량, 자재 회복, 개척포인트 +1
        #     nation = NationBody(nation)

        #     # immune이 0을 초과하면, 1씩 감소
        #     if nation.immune > 0: nation.immune -= 1

        #     nation.settle_point += constants["settle_point_per_turn"]

        #     if not nation.has_block(): continue
        #     # 여기부터는 블럭이 있는 경우만 실행
            
        #     # 블럭 상태가 "safe"면 블럭이 식량과 자재를 생산함
        #     block_food_yield_sum = nation.food_yield()
        #     block_material_yield_sum = nation.material_yield()

        #     # 식량이나 자재가 계산된 각각의 총합보다 적은 경우에만 식량이나 자재를 각 총합으로 변경
        #     if nation.food < block_food_yield_sum: nation.food = block_food_yield_sum
        #     if nation.material < block_material_yield_sum: nation.material = block_material_yield_sum
            
        #     # 안전한 상태의 금광이 있는 경우 사치품을 금광의 수만큼 생산 (없으면 0)
        #     goldmines = self.main_db.fetch_blocks(nation_ID=nation.ID, category="금광", status="safe")

        #     nation.luxury += len(goldmines) * constants["goldmine.luxury_yield"]

        #     nation.update()
        
        # 모든 블럭에 대한 업데이트 사항
        # for block in self.main_db.fetch_all_blocks():

        #     block = BlockBody(block)

        #     # boosted가 0을 초과하면, 1씩 감소
        #     if block.boosted > 0: block.boosted -= 1

        #     # boosted가 0이면, 생산력 원상복구 (0이 되면 다음 턴에 사치품 효과가 적용되지 않으므로)
        #     if block.boosted == 0: block.set_yield_by_defalt()

        #     # 블럭의 상태가 "crisis"인 경우, 타국 부대가 주둔 중이면 소유권이 넘어감

        #     if block.status == "crisis":
        #         encamp_enemy:Troop = self.main_db.fetch("troop", f"location={block.ID} AND nation_ID!={block.nation_ID} AND status != 'moving'")
        #         encamp_ally:Troop = self.main_db.fetch("troop", f"location={block.ID} AND nation_ID={block.nation_ID} AND status != 'moving'")
        #         if encamp_enemy:
        #             block.nation_ID = encamp_enemy.nation_ID
        #             block.status = status.SAFE
        #         elif encamp_ally:
        #             # 아군 부대만 존재하면 상태를 "safe"로 변경
        #             block.status = status.SAFE
            
        #     block.update()

        # 모든 부대에 대한 업데이트 사항
        # for troop in self.main_db.fetch_all_troops():

        #     troop = TroopBody(troop)

        #     # 사치품 부스트 적용

        #     # 부대의 attacked가 1이면 attacked를 0으로 변경
        #     if troop.attacked == 1:
        #         troop.attacked = 0
            
        #     # 부대의 move_to가 None이 아니면, move_to로 이동
        #     if troop.move_to:
        #         troop.location = troop.move_to
        #         troop.move_to = None
        #         troop.status = status.ALERT
            
        #     troop.update()

        # pending 가져와서 처리 (삭제 예정)
        # pendings = self.main_db.fetch_all_pendings()
        # for pending in pendings:
        #     valid = False
        #     if pending.mode == "active":
        #         if pending.execute == schedule.now_turn: valid = True
        #         elif pending.execute < schedule.now_turn: self.main_db.delete_with_id("pending", pending.ID)

        #     elif pending.mode == "passive":
        #         if pending.start <= schedule.now_turn and pending.execute <= schedule.now_turn: valid = True
        #         elif pending.execute < schedule.now_turn: self.main_db.delete_with_id("pending", pending.ID)
            
        #     if valid: 
        #         eval(pending.execute_code)
                
        self.schedule.dump()

    def stop_game(self):
        '''
        게임 중단 함수
        '''

        if self.schedule.state != ScheduleState.WAITING and self.schedule.state != ScheduleState.ONGOING:
            return "게임이 진행 중이 아닙니다."
        
        self.schedule.state = ScheduleState.PAUSED
        self.schedule.dump()

        self.sched.pause_job(ARISLENA_JOB_ID)

        print(f"게임 중단 됨 | {self.schedule.now_turn}일 차")
        return f"게임이 중단 되었습니다. | {self.schedule.now_turn}일 차"

    def end_game(self):
        '''
        게임 종료 함수
        '''
        
        self.schedule.state = ScheduleState.ENDED
        self.schedule.end_date = get_date()

        self.sched.remove_job(ARISLENA_JOB_ID)

        self.schedule.dump()

        print("게임 종료 됨")
        # 게임 종료 메시지 추가 예정
        return "게임이 종료 되었습니다."
