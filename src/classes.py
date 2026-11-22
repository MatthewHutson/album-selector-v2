# -- Imports -- #
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable
from copy import deepcopy
from random import shuffle

# -- Global Variables -- #
SHORT_TIME: int = 60
MEDIUM_TIME: int = 90

# -- Classes -- #
class categories(Enum):
    '''
    Functions to categorise albums by length
    '''
    SHORT: Callable[[int], bool] = (lambda x: x <= SHORT_TIME)
    MEDIUM: Callable[[int], bool]  = (lambda x: x > SHORT_TIME and x <= MEDIUM_TIME)
    LONG: Callable[[int], bool]  = (lambda x: x > MEDIUM_TIME)

@dataclass
class Album():
    '''An object representation of a single ablum'''
    # -- Attributes -- #
    name: str
    artist: str
    length: int # -- Minutes
    year: int = None
    listen_count : int = 0

    # -- Properties -- #
    @property
    def time(self) -> str:
        hours: int = str(self.length // 60)
        minutes: int = str(self.length % 60)

        if len(minutes) == 1:
            minutes = "0" + minutes

        return f"{hours}:{minutes}"

    # -- Methods -- #
    def __str__(self) -> str:
        return f"{self.artist} - {self.name}"

    def __len__(self) -> int:
        return self.length

    def __lt__(self, other: Album) -> bool:
        if self.length == other.length:
            if self.artist == other.artist:
                return self.name < other.name

            return self.artist < other.artist

        return self.length < other.length

    def __gt__(self, other: Album):
        if self.length == other.length:
            if self.artist == other.artist:
                return self.name > other.name
        
            return self.artist > other.artist
        
        return self.length > other.length

    def __eq__(self, other: Album):
        data_1, data_2 = deepcopy(self.__dict__), deepcopy(other.__dict__)
        data_1["listen_count"] = data_2["listen_count"] = 0

        return data_1 == data_2

class Manager():
    '''An onbect to store a collection of albums'''
    # -- Attribures -- #
    albums: list[Album]

    # -- Properties -- #
    @property
    def short(self) -> list[Album]:
        albums = [album for album in self.albums if categories.SHORT(album.length)]
        shuffle(albums)
        return albums

    @property
    def medium(self) -> list[Album]:
        albums = [album for album in self.albums if categories.MEDIUM(album.length)]
        shuffle(albums)
        return albums

    @property
    def long(self) -> list[Album]:
        albums = [album for album in self.albums if categories.LONG(album.length)]
        shuffle(albums)
        return albums

    @property
    def artists(self) -> list[str]:
        artists: list[str] = list({album.artist for album in self.albums})
        artists.sort()
        return artists
    
    # -- Methods -- #
    def sort(self, reverse: bool = False) -> None:
        '''Sorts the albums by length'''
        self.albums.sort(reverse = reverse)

    def add(self, album: Album) -> None:
        if not album in self.albums:
            self.albums.append(album)
            self.sort()

    def get_albums(self, name: str, artist: str) -> list[Album]:
        return [album for album in self.albums if album.name == name and album.artist == artist]

    def remove(self, album: Album) -> None:
        self.albums.remove(album)

    def __init__(self, albums: list[Album] = []) -> None:
        self.albums = albums
        self.sort()

    def __str__(self) -> int:
        '''Outputs a table of the allbums stored in the manager.'''
        name_header, artist_header = "Album Name", "Artist"
        max_len_name, max_len_artist = len(name_header), len(artist_header)

        for album in self.albums:
            if len(album.name) > max_len_artist:
                max_len_name = len(album.name)

            if len(album.artist) > max_len_artist:
                max_len_artist = len(album.artist)

        max_len_name += 5
        max_len_artist += 5

        out = f"  {artist_header:<{max_len_artist}} {name_header:<{max_len_name}} Length"

        for album in self.albums:
            out += "\n  " + f"{album.artist:<{max_len_artist}} {album.name:<{max_len_name}} {album.time}"

        return out
    
# -- Testing -- #
if __name__ == "__main__":
    test_album = Album("test", "test", 60)
    test_album_2 = Album("long_album_name............................................", "test_2", 90)
    test_album_3 = Album("test_2", "long_artist_name..............................", 200)

    manager = Manager([test_album, test_album_3])

    print()
    print(manager)

    manager.add(test_album_2)

    print()
    print(manager)

    manager.add(deepcopy(test_album_2))
    
    print()
    print(manager)
    print()
    print(manager.artists)
    print(manager.short)
    print(manager.medium)
    print(manager.long)