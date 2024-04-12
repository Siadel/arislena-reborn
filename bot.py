import traceback, discord, os, asyncio
from typing import Union
from discord import app_commands

from py_base import utility 
from py_base.dbmanager import DatabaseManager
from py_system._global import bot_setting
from py_system.tableobj import form_database_from_tableobjects
from py_discord import warnings
from py_discord.bot_base import BotBase, ScheduleManager
from py_discord.checks import is_admin

class AriBot(BotBase):
    
    def __init__(self, bot_setting):
        super().__init__(bot_setting)
        self._ready_flag = False
        
    async def setup_hook(self):
        for file in os.listdir(utility.current_path + "cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
        await aribot.tree.sync(guild=discord.Object(id=bot_setting.main_guild_id))
        await aribot.tree.sync(guild=discord.Object(id=bot_setting.test_guild_id))
        
    async def on_ready(self):
        await self.wait_until_ready()
        await self.change_presence(status=discord.Status.online, activity=discord.Game("아리슬레나 가꾸기"))
        
        for guild in self.guilds:
            self._add_database_and_scheduler(guild.id)
        
        if not self._ready_flag: # 테스트용 데이터베이스가 아닐 경우에만 봇 입장 메시지 출력
            for guild in self.guilds:
                if self._guild_schedule[str(guild.id)].game_setting.test_mode: continue
                await self.announce(f"아리가 {guild.name}에 들어왔어요!", guild.id)
            self._ready_flag = True

        # 정보 출력
        print(f"discord.py version: {discord.__version__}")
        print(f'We have logged in as {self.user}')

    async def close(self):
        for guild in self.guilds:
            await self.announce(f"아리가 {guild.name}에서 나가요!", guild.id)
        await super().close()

# 봇 객체 생성
aribot = AriBot(bot_setting)

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
    line = f"{utility.get_date(utility.DATE_EXPRESSION_FULL)}\t{interaction.user.id}\t{interaction.user.name}\t{interaction.user.nick}\t{interaction.data['name']}\t{command.name}"
    print(line)
    log_file = open("command_log.txt", "a", encoding="utf-8")
    log_file.write(line + utility.ENTER)
    log_file.close()

# 기타 명령어

@aribot.tree.command(
    name = "종료",
    description = "봇을 공식적으로 종료합니다. ⚠ 프리시즌 테스트 기간이거나, 기능 테스트 목적이 아니면 비상 시에만 사용해야 합니다.",
    guilds=aribot.guilds
)
async def exit_bot(interaction: discord.Interaction):
    if not is_admin(interaction): raise warnings.NotAdmin()
    await interaction.response.send_message("봇을 종료합니다.", ephemeral=True)
    await aribot.close()

@aribot.tree.command(
    name = "턴넘기기",
    description = "턴을 넘깁니다. ⚠ 프리시즌 테스트 기간이거나, 기능 테스트 목적이 아니면 비상 시에만 사용해야 합니다.",
    guilds=aribot.guilds
)
async def elapse_turn(interaction: discord.Interaction):
    if not is_admin(interaction): raise warnings.NotAdmin()
    await aribot.guild_schedule[interaction.guild_id].end_turn()
    await interaction.response.send_message(f"턴이 넘어갔습니다. (현재 턴: {aribot.guild_schedule[interaction.guild_id].chalkboard.now_turn})")


if __name__ == "__main__":
    # 봇 실행
    aribot.run()
