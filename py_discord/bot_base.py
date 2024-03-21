import discord, logging, json
from discord.ext import commands
from os import environ, path

from py_system._global import setting_by_guild, bot_setting, game_setting, job_setting, main_db, schedule
from py_system.schedule_manager import ScheduleManager
from py_system.tableobj import form_database_from_tableobjects

# 봇 권한 설정
intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.members = True

form_database_from_tableobjects(main_db)

schedule_manager = ScheduleManager(main_db, schedule, game_setting, job_setting)

def exit_bot():
    print("봇을 종료합니다.")
    exit(1)

class BotBase(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="/",
            intents=intents,
            application_id=bot_setting.application_id)
        
        self.objectified_guilds = [discord.Object(id=ID) for ID in bot_setting.guild_ids]
        self.token = environ.get("ARISLENA_BOT_TOKEN")
        self.log_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

        if not self.token: 
            print("환경 변수에 ARISLENA_BOT_TOKEN이 없습니다. json/token.json 파일을 확인합니다.")
            if not path.exists("json/token.json"):
                print("json/token.json 파일이 없습니다.")
                exit_bot()
            with open("json/token.json", "r", encoding="utf-8") as f:
                self.token = json.load(f).get("ARISLENA_BOT_TOKEN")
            if self.token is None:
                print("json/token.json 파일에 ARISLENA_BOT_TOKEN이 없습니다.")
                exit_bot()

    async def announce(self, message:str, guild_id:int):
        """
        지정된 봇 전용 공지 채널에 메세지를 보냄. 지정 채널이 없으면 아무것도 하지 않음.
        """
        if (guild_id_key := str(guild_id)) in setting_by_guild.announce_location:
            
            channel = self.get_channel(setting_by_guild.announce_location[guild_id_key])
            await channel.send(message)
    
    def run(self):
        super().run(self.token, log_handler=self.log_handler, log_level=logging.INFO)

