import traceback, discord
from typing import Union
from discord import app_commands

from py_base.utility import CWD
from py_base.ari_logger import ari_logger
from py_system._global import bot_setting
from py_discord import warnings
from py_discord.bot_base import BotBase

class AriBot(BotBase):
    
    def __init__(self, bot_setting):
        super().__init__(bot_setting)
        self._ready_flag = False
        
    async def setup_hook(self):
        for file in (CWD / "cogs").iterdir():
            if file.is_file() and file.suffix == ".py":
                await self.load_extension(f"cogs.{file.stem}")
        
    async def on_ready(self):
        await self.wait_until_ready()
        await self.change_presence(status=discord.Status.online, activity=discord.Game("아리슬레나 가꾸기"))
        
        for guild in self.guilds:
            self._add_server_manager(guild.id)
        
        if not self._ready_flag: # 테스트용 데이터베이스가 아닐 경우에만 봇 입장 메시지 출력
            for guild in self.guilds:
                if self.get_server_manager(guild.id).chalkboard.test_mode: continue
                await self.announce_channel(f"아리가 {guild.name}에 들어왔어요!", self.get_server_manager(guild.id).guild_setting.announce_channel_id)
            self._ready_flag = True

        # 슬래시 명령어 동기화
        main_sync_result = await aribot.tree.sync(guild=self.main_guild)
        ari_logger.info(f"Slash commands synced in main guild: {main_sync_result}")
        # test_sync_result = await aribot.tree.sync(guild=self.test_guild)
        # ari_logger.info(f"Slash commands synced in test guild: {test_sync_result}")
        global_sync_result = await aribot.tree.sync()
        ari_logger.info(f"Slash commands synced globally: {global_sync_result}")
        
        # 정보 출력
        ari_logger.info(f"discord.py version: {discord.__version__}")
        ari_logger.info(f'We have logged in as {self.user}')
        ari_logger.info(f"Registered commands: {await aribot.tree.fetch_commands()}")

    async def close(self):
        for guild in self.guilds:
            await self.announce_channel(f"아리가 {guild.name}에서 나가요!", guild.id)
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
        ari_logger.warning(traceback.format_exc())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        ari_logger.error(traceback.format_exc())
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("오류가 발생했습니다. 관리자에게 문의해주세요!", ephemeral=True)


# 명령어가 정상적으로 실행되었을 때 정보 기록
@aribot.event
async def on_app_command_completion(interaction: discord.Interaction, command: Union[app_commands.Command, app_commands.ContextMenu]) -> None:
    # 명령어 사용자, 닉네임, 명령어 이름, 명령어 인자
    # tab을 기준으로 정렬
    line = f"user id: {interaction.user.id}\n\tuser name: {interaction.user.name}\n\tuser nick: {interaction.user.nick}\n\tinteraction data: {interaction.data['name']}\n\tcommand: {command.name}"
    ari_logger.info(line)


# 기타 명령어

@aribot.tree.command(
    name = "동기화",
    description = "명령어를 동기화합니다."
)
async def sync(interaction: discord.Interaction):
    sync_result = await aribot.tree.sync()
    await interaction.response.send_message(f"Slash commands synced: {sync_result}", ephemeral=True)

@aribot.tree.command(
    name = "종료",
    description = "봇을 공식적으로 종료합니다. ⚠ 프리시즌 테스트 기간이거나, 기능 테스트 목적이 아니면 비상 시에만 사용해야 합니다.",
    guild=aribot.main_guild
)
async def exit_bot(interaction: discord.Interaction):
    aribot.check_admin_or_raise(interaction)
    await interaction.response.send_message("봇을 종료합니다.", ephemeral=True)
    await aribot.close()

@aribot.tree.command(
    name = "턴넘기기",
    description = "턴을 넘깁니다. ⚠ 프리시즌 테스트 기간이거나, 기능 테스트 목적이 아니면 비상 시에만 사용해야 합니다."
)
async def elapse_turn(interaction: discord.Interaction):
    aribot.check_admin_or_raise(interaction)
    await aribot.get_server_manager(interaction.guild_id).end_turn()
    await interaction.response.send_message(f"턴이 넘어갔습니다. (현재 턴: {aribot.get_server_manager(interaction.guild_id).chalkboard.now_turn})")


if __name__ == "__main__":
    # 봇 실행
    aribot.run()
    