import discord
from discord.ext import commands
from discord import app_commands

from py_system import jsonobj

# 길드 id와 봇 토큰
keys = jsonobj.Keys()

# 봇 권한 설정
intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.members = True

class BotBase(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="/",
            intents=intents,
            application_id=keys.application_id)
        
        self.token = keys.token
        self.objectified_guilds = [discord.Object(id=ID) for ID in keys.guild_ids]

    async def announce(self, message:str):
        # "아리"라는 채널에 메세지를 보냅니다.
        channel = self.get_channel(jsonobj.Settings().content["announce_channel_id"])
        await channel.send(message)

