# -- Imports -- #
from __future__ import annotations
from dotenv import load_dotenv
from bot import *
from cogs import *

# -- Global Objects -- #
client = BotHandler()

# -- Adding Cogs -- #
client.add_cog(UserCommands())

# -- Events -- #
@client.event
async def on_ready() -> None:
    await client.set_log()
    await client.set_admin()
    loaded_message: str = f'{client.user} has connected to Discord!\n'
    await client.log(loaded_message)

# -- Main -- #
if __name__ == "__main__":
    load_dotenv()
    client.activate()
