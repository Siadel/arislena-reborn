import traceback, os, discord
from typing import Union
from discord import app_commands
from py import database, utility, warning, schedule_manager, jsonobj, tableobj, translation
from py.bot_base import BotBase

db = database.MainDB()
schem = schedule_manager.ScheduleManager(db, jsonobj.Schedule(), jsonobj.Settings())

"""
TableObject 객체를 상속하는 객체의 수만큼 테이블 생성하고, 테이블을 초기화함
만약 TableObject를 상속하는 객체의 데이터 형식이 기존의 데이터 형식과 다를 경우, 기존의 데이터를 유지하며 새로운 데이터 형식을 추가해야 함
"""
for subclass in tableobj.TableObject.__subclasses__():
    # TableObject를 상속하는 객체의 테이블을 생성함 (이미 존재할 경우, 무시함)
    db.cursor.execute(subclass.get_create_table_string())

    table_name = subclass.get_table_name()
    # TableObject를 상속하는 객체의 데이터 형식과 db의 데이터 형식을 불러와 차이를 판별하기
    # db의 데이터 형식을 불러옴
    sql_table_column_set = db.table_column_set(table_name)

    # TableObject를 상속하는 객체의 데이터 형식을 불러옴
    tableobj_column_set = subclass.get_column_set()

    # 데이터베이스 테이블의 데이터 형식과 TableObject를 상속하는 객체의 데이터 형식을 비교함
    # TableObject를 상속하는 객체에 없는 데이터 형식이 있을 경우, db에서 해당 데이터 형식을 삭제함
    # db에 없는 데이터 형식이 있을 경우, db에 해당 데이터 형식을 추가함
        # 이 경우 추가로 column 순서를 맞추기 위해 테이블을 재생성함
    for column_name in (tableobj_column_set - sql_table_column_set):
        db.cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
    
    table_recreate = False
    if set(sql_table_column_set) != set(tableobj_column_set): table_recreate = True
    
    # 테이블을 재생성해야 하는 경우
    if table_recreate:
        has_row = db.has_row(table_name)
        if has_row:
            # 테이블 데이터 백업
            # 테이블에 데이터가 없는 경우 백업할 필요 없음
            db.cursor.execute(f"CREATE TABLE {table_name}_backup AS SELECT * FROM {table_name}")
        # 테이블 삭제
        db.cursor.execute(f"DROP TABLE {table_name}")
        # 테이블 재생성
        db.cursor.execute(subclass.get_create_table_string())
        if has_row:
            # 백업 테이블의 column마다 작업하여 테이블 데이터 복원
            # 백업 테이블의 데이터를 {key:value} 형식으로 변환함
            db.cursor.execute(f"SELECT * FROM {table_name}_backup")
            backup_data = [dict(zip([column[0] for column in db.cursor.description], data)) for data in db.cursor.fetchall()]
            # 백업 테이블의 데이터를 새로운 테이블에 삽입함
            for data in backup_data:
                db.insert(subclass(**data))
            # 백업 테이블 삭제
            db.cursor.execute(f"DROP TABLE {table_name}_backup")
del db
print("Database initialized")

# 봇 객체 선언
class AriBot(BotBase):

    def __init__(self):

        super().__init__()

    async def setup_hook(self):
        for file in os.listdir(utility.current_path + "cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")
        keys = jsonobj.Keys()
        await aribot.tree.sync(guild=discord.Object(id=keys.main_guild_id))

    async def on_ready(self):
        await self.wait_until_ready()
        await self.change_presence(status=discord.Status.online, activity=discord.Game("아리슬레나 가꾸기"))
    
        print(f'We have logged in as {self.user}')

    async def close(self):
        await super().close()

# 봇 객체 생성
aribot = AriBot()

# 명령어 오류 핸들링
@aribot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:

    is_warning = False
    if isinstance(error, discord.app_commands.CommandInvokeError) and isinstance(error.original, warning.Default):
        is_warning = True
        # 주황색
        embed_color = 0xe67e22
        word = "경고"
        error_name = type(error.original).__name__

        embed_name = f"`/{error.command.name}` 명령어에서 {error_name} {word}가 발생했습니다."
        embed_value = error.original.__str__()

    else:
        # 빨간색
        embed_color = 0xe74c3c
        word = "오류"
        error_name = type(error).__name__

        embed_name = f"{error_name} {word}가 발생했습니다."
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
