# -- Imports -- #
import discord
from bot import *
from classes import *
from loading import *
from selector_functions import *

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
    # -- Methods -- #
    def positive_integer_check(self, data: str) -> bool:
        if data.isdigit():
            num = int(data)
            if num >= 0:
                return True

        return False
    
    def get_album(self, id: int, name: str, artist: str) -> Album | None:
        data: Manager = load_albums(id)
        possible_albums: list[Album] = data.get_albums(name, artist)

        match len(possible_albums):
            case 0: return None
            case 1: return possible_albums[0]
            case _: raise LookupError(f"Multiple albums called {name} by {artist} are present in your save when they shouldn't be!")

    # -- Cog Commands -- #
    @discord.Cog.listener()
    async def on_ready(self) -> None:
        print("User Commands Cog is loaded")
        
    @discord.slash_command(description='Suggest a short, medium or long album to listen to.')
    async def suggest(self, ctx: discord.ApplicationContext) -> None:
        global command_count

        user: discord.User = ctx.author
        data: Manager = load_albums(user.id)
        command_count += 1
    
        await ctx.respond('Select an option:', view=AlbumView(text = "Make A Choice", data = data))
        command_count =- 1

    @discord.slash_command(description='Add a new album to the save (with a length in minutes)')
    async def add(self, ctx: discord.ApplicationContext, album_name: str, artist: str, length: str, year: str) -> None:
        global command_count
    
        user: discord.User = ctx.author
        album: Album | None = self.get_album(user.id, album_name, artist)
        command_count += 1

        if not self.positive_integer_check(length):
            await ctx.respond('ERROR: The album length is not an positive integer number of minutes!')

        elif not self.positive_integer_check(year):
            await ctx.respond('ERROR: The album release year is not an positive integer number of minutes!')

        else:
            if album is None: 
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
        album: Album | None = self.get_album(user.id, album_name, artist)
        command_count += 1

        if album is not None:
            data.remove(album)
            save_data(user.id, data)
            await ctx.respond(f"The album `{album_name}` by `{artist}` has been removed from your save!")
        else:
            await ctx.respond(f"No album named `{album_name}` and released by `{artist}` exists in your save!")
                
        command_count =- 1

    @discord.slash_command(description= 'Count the number of albums you have saved. You can filter this by artist.')
    async def count(self, ctx: discord.ApplicationContext, artist: str = None) -> None:
        global command_count
            
        user: discord.User = ctx.author
        data: Manager = load_albums(user.id)
        command_count += 1

        if artist is None:
            count = len(data)
            await ctx.respond(f"You have `{count}` albums in your save!")
        else:
            count = len(data.filter(artist))
            await ctx.respond(f"You have `{count}` albums by `{artist}` in your save!")

        command_count =- 1

    @discord.slash_command(description = 'Increment the number of listens of a specific album by any amount (default count is 1)')
    async def increment(self, ctx: discord.ApplicationContext, album_name: str, artist: str, count: int = 1) -> None:
        global command_count

        user: discord.User = ctx.author
        manager: Manager = load_albums(user.id)
        album: Album | None = self.get_album(user.id, album_name, artist)
        command_count += 1

        if album is None:
            await ctx.respond(f"No album named `{album_name}` and released by `{artist}` exists in your save!") 
        else:
            album.listen_count += count
            save_data(user.id, manager)
            await ctx.respond(f"`{count}` listen{"s" if count != 1 else ""} has been added to your save of `{album_name}` by `{artist}`!") 

        command_count =- 1

    @discord.slash_command(description = 'Show how many hours and minutes of music you have logged listening to with this bot!')
    async def listen_time(self, ctx: discord.ApplicationContext) -> None:
        global command_count

        user: discord.User = ctx.author
        data: Manager = load_albums(user.id)
        total: int = 0
        command_count += 1

        for album in data.albums:
            total += album.listen_count * album.length

        hours: int = total // 60
        minutes: int = total % 60
        minutes: str = "0" + str(minutes) if minutes < 10 else str(minutes)

        await ctx.respond(f"Using this bot, you have logged a total listen time of `{hours}:{minutes}` (`h:m`)!")

    @discord.slash_command(description = 'Display any number of most listened to artist (default number is 3)')
    async def top_artists(self, ctx: discord.ApplicationContext, num: int = 3) -> None:
        global command_count

        if num > 0:
            # -- Discord & Loading Data -- #
            user: discord.User = ctx.author
            data: Manager = load_albums(user.id)
            command_count += 1

            # -- Determining Top Artists
            artist_time: dict[str, int] = {artist: 0 for artist in data.artists}

            for artist in artist_time.keys():
                for album in data.albums:
                    if artist == album.artist:
                        artist_time[artist] += album.listen_count * album.length

            sorted_artist_time: dict[str, int] = {artist: time for artist, time in sorted(artist_time.items(), key = lambda item: item[1], reverse = True)}
            artists = list(sorted_artist_time.keys())
            top_artists = artists[:num]

            # -- Output Data -- #
            output: str = f"The top `{num}` most listened to artist{"s" if num != 1 else ""} in your save are:"
            ordering: list[tuple[str, str]] = []

            for i in range(len(top_artists)):
                artist = top_artists[i]
                total_mins: int = artist_time[artist]

                hours: int = total_mins // 60
                minutes: int = total_mins % 60
                minutes: str = "0" + str(minutes) if minutes < 10 else str(minutes)

                line: str = f"`{artist}` - `{hours}:{minutes}` (`h:m`)"
                ordering.append((f"{i + 1}.", line))

            embed = discord.Embed(title = "Most Listened to Artists", description = output, color = discord.Color.blurple())

            for index, text in ordering:
                embed.add_field(name = index, value = text, inline = True)
                embed.add_field(name = "", value = "", inline = False)

            await ctx.respond(embed = embed)

        else:
            await ctx.respond("**Invalid Argument**: num has to be a positive integer!")