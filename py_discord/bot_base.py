import discord, logging, json, os
from discord.ext import commands
from copy import deepcopy

from py_base.ari_logger import ari_logger
from py_base.dbmanager import DatabaseManager
from py_base.utility import JSON_DIR
from py_base.jsonobj import BotSetting
from py_system.tableobj import form_database_from_tableobjects
from py_discord import warnings
from py_discord.server_manager import ServerManager

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
        self
    ):
        bot_setting = BotSetting.from_json_file()

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
        
        self._guild_server_manager: dict[str, ServerManager] = {}
    
    def get_database(self, guild_id: int | str) -> DatabaseManager:
        """
        usage example:
        ```
        bot.get_database(interaction.guild_id)
        ```
        """
        return self._guild_server_manager[str(guild_id)].database
    
    def get_server_manager(self, guild_id: int | str) -> ServerManager:
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
            
            ari_logger.warning("환경 변수에 ARISLENA_BOT_TOKEN이 없습니다. json/token.json 파일을 확인합니다.")
            token_return: str = None
            token_file = JSON_DIR / "token.json"
            
            if not token_file.exists():
                ari_logger.critical(f"지정된 경로 {token_file}에 파일이 없습니다.")
                exit_bot()
            
            with open(token_file, "r", encoding="utf-8") as f:
                if (token_return := json.load(f).get("ARISLENA_BOT_TOKEN")) is None:
                    ari_logger.critical(f"지정된 파일 {token_file}에 ARISLENA_BOT_TOKEN이 없습니다.")
                    exit_bot()
                    
            return token_return
        
        else: return environ_get_result
    
    async def announce_channel(self, message:str, guild_id:int):
        """
        지정된 채널에 메세지를 보냄.
        """
        if (channel := self.get_channel(guild_id)) is None: ari_logger.error(f"길드 id {guild_id}의 채널을 찾을 수 없습니다.")
        await channel.send(message)
    
    async def announce_channel_with_embed(self, embed:discord.Embed, guild_id:int):
        """
        지정된 채널에 embed를 보냄.
        """
        if (channel := self.get_channel(guild_id)) is None: ari_logger.error(f"길드 id {guild_id}의 채널을 찾을 수 없습니다.")
        await channel.send(embed=embed)

    def run(self):
        super().run(self._token, log_handler=self._log_handler, log_level=logging.INFO)
    
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
            raise warnings.AlreadyRegistered()
        
    def check_user_exists(self, interaction: discord.Interaction) -> bool:
        """
        아리슬레나에 등록되어 있는지 확인하는 함수
        """
        if not self.get_database(interaction.guild_id).is_exist("user", discord_id=interaction.user.id):
            return False
        return True

