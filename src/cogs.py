# -- Imports -- #
import discord
from bot import *
from classes import *
from loading import *
from selector_functions import *
from dotenv import load_dotenv
import subprocess

# -- Global Data -- #
command_count = 0

# -- Objects -- #
class AlbumSelect(discord.ui.Select):
    def __init__(self, text: str, data: Manager) -> None:
        global command_count

        self.data = data
        self.selections: Manager = output_selection(data)
        self.made_selection = False

        command_count += 1
        
        self.selection_data: dict[str, Album] = {str(album): album for album in self.selections.albums}
        self.selection_data["reroll"] = None
        self.selection_data["cancel"] = None

        options = [discord.SelectOption(label = album_str) for album_str in self.selection_data.keys()]

        super().__init__(placeholder = text, options = options)

    async def callback(self, interaction: discord.Interaction) -> None:
        global command_count

        if not self.made_selection:
            result: str = self.values[0]
            user: discord.User = interaction.user
            self.made_selection = True

            await interaction.response.send_message(f'You selected `{result}`!')

            match result:
                case "reroll":
                    channel = await user.create_dm()
                    await channel.send('Select an option:', view = AlbumView(text = "Make A Choice", data = self.data))
                case "cancel": pass
                case _:
                    album: Album = self.selection_data[result]
                    album.listen_count += 1
                    save_data(user.id, self.data)

        command_count -= 1

class AlbumView(discord.ui.View):
    def __init__(self, text: str, data: Manager) -> None:
        super().__init__()
        self.add_item(AlbumSelect(text = text, data = data))

class UserCommands(discord.Cog):
    def positive_integer_check(self, data: str) -> bool:
        if data.isdigit():
            num = int(data)
            if num >= 0:
                return True

        return False

    @discord.Cog.listener()
    async def on_ready(self) -> None:
        print("User Commands Cog is loaded")
        
    @discord.slash_command(description='Suggest a short, medium or long album to listen to.')
    async def suggest(self, ctx: discord.ApplicationContext) -> None:
        global command_count

        user: discord.User = ctx.author
        data: Manager = load_albums(user.id)
        command_count += 1
    
        channel = await user.create_dm()
        await ctx.respond('Select an option:', view=AlbumView(text = "Make A Choice", data = data))
        command_count =- 1

    @discord.slash_command(description='Add a new album to the save (with a length in minutes)')
    async def add(self, ctx: discord.ApplicationContext, album_name: str, artist: str, length: str, year: str) -> None:
        global command_count
    
        user: discord.User = ctx.author
        data: Manager = load_albums(user.id)
        command_count += 1

        channel = await user.create_dm()

        if not self.positive_integer_check(length):
            await ctx.respond('ERROR: The album length is not an positive integer number of minutes!')

        elif not self.positive_integer_check(year):
            await ctx.respond('ERROR: The album release year is not an positive integer number of minutes!')

        else:
            if len(data.get_albums(album_name, artist)) == 0: 
                album = Album(album_name, artist, int(length), int(year))
                data.add(album)
                save_data(user.id, data)
                await ctx.respond(f"The album `{album_name}` by `{artist}` has been added to your save!")
            else:
                await ctx.respond(f"The album `{album_name}` by `{artist}` already exists in your save!")
            
        command_count =- 1

    @discord.slash_command(description='Remove an Album')
    async def remove(self, ctx: discord.ApplicationContext, album_name: str, artist: str) -> None:
        global command_count
        
        user: discord.User = ctx.author
        data: Manager = load_albums(user.id)
        command_count += 1
    
        channel = await user.create_dm()
        album_list = data.get_albums(album_name, artist) # -- Only Length 1 or 0

        if len(album_list) == 1:
            album = album_list[0]
            data.remove(album)
            save_data(user.id, data)
            await ctx.respond(f"The album `{album_name}` by `{artist}` has been removed from your save!")
        else:
            await ctx.respond(f"No album names `{album_name}` and released by `{artist}` exists in your save!")
                
        command_count =- 1
