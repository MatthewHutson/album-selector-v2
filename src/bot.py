# -- Imports -- #
from __future__ import annotations
import discord
from discord.ext import commands
import os 

# -- Classes -- #
class BotHandler(commands.Bot):
    # -- Attributes -- #
    log_channel: discord.abc.Guild | discord.Thread | discord.abc.PrivateChannel
    admin: discord.User

    # -- Properties -- #
    @property
    def TOKEN(self) -> str: return os.getenv('TOKEN')

    @property
    def LOG(self) -> str: return os.getenv('LOG')

    @property
    def ADMIN(self) -> str: return os.getenv('ADMIN')
    
    # -- Methods -- #
    def __init__(self, *, loop = None, **options):
        # -- Intents -- #
        intents = discord.Intents()
        intents.polls = True
        intents.messages = True
        intents.guilds = True

        # -- Other -- #
        super().__init__(loop=loop, intents = intents, **options)

    def activate(self):
        self.run(self.TOKEN)

    async def set_log(self):
        channel = await self.fetch_channel(self.LOG)
        self.log_channel = channel

    async def set_admin(self):
        admin = await self.fetch_user(self.ADMIN)
        self.admin = admin

    async def log(self, message: str) -> None:
        await self.log_channel.send(message)