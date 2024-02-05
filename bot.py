import traceback, os, discord
from typing import Union
from discord import app_commands

from py_discord import warnings
from py_discord.bot_base import BotBase

from py_base import utility 
from py_system.tableobj import form_database_from_tableobjects
from py_system.global_ import main_db, keys

form_database_from_tableobjects(main_db)

# 봇 객체 선언
class AriBot(BotBase):

    def __init__(self):

        super().__init__()

    async def setup_hook(self):
        for file in os.listdir(utility.current_path + "cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
        await aribot.tree.sync(guild=discord.Object(id=keys.main_guild_id))

    async def on_ready(self):
        await self.wait_until_ready()
        await self.change_presence(status=discord.Status.online, activity=discord.Game("아리슬레나 가꾸기"))

        # 정보 출력
        print(f"discord.py version: {discord.__version__}")
        print(f'We have logged in as {self.user}')

    async def close(self):
        await super().close()

# 봇 객체 생성
aribot = AriBot()

# 명령어 오류 핸들링
@aribot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:

    is_warning = False
    if isinstance(error, discord.app_commands.CommandInvokeError) and isinstance(error.original, warnings.Default):
        is_warning = True
        # 주황색
        embed_color = 0xe67e22
        error_name = type(error.original).__name__

        embed_name = f"{error_name} 경고가 발생했습니다."
        embed_value = error.original.__str__()

    else:
        # 빨간색
        embed_color = 0xe74c3c
        error_name = type(error).__name__

        embed_name = f"{error_name} 오류가 발생했습니다."
        embed_value = f"`{error.__str__()}`"

        print(traceback.format_exc()) # 오류 출력
    
    embed = discord.Embed(color=embed_color)
    embed.add_field(name=embed_name, value=embed_value)

    if is_warning:
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        # 오류일 경우만 error_log.txt에 오류 내용 저장
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{utility.get_date(utility.DATE_EXPRESSION_FULL)} : {error}{utility.ENTER}")
            f.write(traceback.format_exc())
            f.write(utility.ENTER)
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("오류가 발생했습니다. 관리자에게 문의해주세요!", ephemeral=True)


# 명령어가 정상적으로 실행되었을 때 정보 기록
@aribot.event
async def on_app_command_completion(interaction: discord.Interaction, command: Union[app_commands.Command, app_commands.ContextMenu]) -> None:
    # 사용 시간, 명령어 사용자, 닉네임, 명령어 이름, 명령어 인자
    # tab을 기준으로 정렬
    log_file = open("command_log.txt", "a", encoding="utf-8")
    log_file.write(f"{utility.get_date(utility.DATE_EXPRESSION_FULL)}\t{interaction.user.id}\t{interaction.user.name}\t{interaction.user.nick}\t{interaction.data['name']}\t{command.name}\n{interaction.data}\n")
    log_file.close()

if __name__ == "__main__":

    # 봇 실행
    aribot.run(aribot.token)
