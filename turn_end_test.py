import asyncio
from py_discord.schedule_manager import ScheduleManager
from bot import aribot
from py_system._global import main_db, bot_setting, schedule, game_setting, job_setting

schedule_manager = ScheduleManager(
    aribot, bot_setting, main_db, schedule, game_setting, job_setting
)

def main():
    
    result_list = schedule_manager.building_produce()
    print(f"result: {result_list}")
    
    for result_embed in result_list:
        print(f"embed title: {result_embed.title}")
        for field in result_embed.fields:
            print(f"field name: {field.name}")
            print(f"field value: {field.value}")

if __name__ == '__main__':
    main()