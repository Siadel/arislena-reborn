import traceback, discord
from typing import Union
from discord import app_commands

from py_base import utility 

from py_system._global import bot_setting
from py_discord import warnings
from py_discord.bot_base import AriBot
from py_discord.checks import is_admin

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
    guilds=aribot._guild_list
)
async def exit_bot(interaction: discord.Interaction):
    if not is_admin(interaction): raise warnings.NotAdmin()
    await interaction.response.send_message("봇을 종료합니다.", ephemeral=True)
    await aribot.close()

@aribot.tree.command(
    name = "턴넘기기",
    description = "턴을 넘깁니다. ⚠ 프리시즌 테스트 기간이거나, 기능 테스트 목적이 아니면 비상 시에만 사용해야 합니다.",
    guilds=aribot._guild_list
)
async def elapse_turn(interaction: discord.Interaction):
    if not is_admin(interaction): raise warnings.NotAdmin()
    await aribot.guild_schedule[interaction.guild_id].end_turn()
    await interaction.response.send_message(f"턴이 넘어갔습니다. (현재 턴: {aribot.guild_schedule[interaction.guild_id].chalkboard.now_turn})")


if __name__ == "__main__":
    # 봇 실행
    aribot.run()
