import asyncio
import datetime
import threading
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def some_job_function():
    print(f"{datetime.datetime.now()} some job executed")
    
async def another_job_function():
    print(f"{datetime.datetime.now()} another job executed")

def create_scheduler_with_new_event_loop():
    new_loop = asyncio.new_event_loop()
    scheduler = AsyncIOScheduler(event_loop=new_loop)
    return scheduler, new_loop

# 비동기 함수로 스케줄러를 별도의 스레드나 비동기 컨텍스트에서 실행
async def run_scheduler(scheduler, loop):
    asyncio.set_event_loop(loop)
    scheduler.start()
    
def run_loop_forever(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# 각 이벤트 루프를 별도의 스레드나 비동기 태스크에서 실행할 수 있습니다.
# 예를 들어, 각 이벤트 루프를 별도의 asyncio.Task로 실행할 수 있습니다.

if __name__ == "__main__":
    
    # 스케줄러 및 이벤트 루프 생성
    scheduler1, loop1 = create_scheduler_with_new_event_loop()
    scheduler2, loop2 = create_scheduler_with_new_event_loop()

    # 각 스케줄러에 작업 추가
    scheduler1.add_job(some_job_function, 'interval', seconds=3)
    scheduler2.add_job(another_job_function, 'interval', seconds=5)

    # 스케줄러 실행 태스크 생성
    loop1.create_task(run_scheduler(scheduler1, loop1))
    loop2.create_task(run_scheduler(scheduler2, loop2))

    # 각 이벤트 루프를 별도의 스레드에서 실행
    thread1 = threading.Thread(target=run_loop_forever, args=(loop1,))
    thread2 = threading.Thread(target=run_loop_forever, args=(loop2,))
    thread1.start()
    thread2.start()

    # 필요시 스레드 조인
    thread1.join()
    thread2.join()