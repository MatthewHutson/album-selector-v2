# -- Imports -- #
from classes import *
import json
import os

# -- Functions -- #
def existance(id: int) -> None:
    '''Creates a file for a user_id if not present'''

    path: str = f"albums/{id}.json"

    if not os.path.isfile(path):
        with open(path, "w") as file:
            json.dump([], file, indent = 4)

def load_albums(id: int) -> Manager:
    existance(id)

    with open(f"albums/{id}.json", "r") as file:
        load_data: list[dict] = json.load(file)
        data = Manager()

        for instance in load_data:
            album = Album(**instance)
            data.add(album)
    
    return data

def create_poll_data(data: Manager) -> dict[str, Album]:
    return {str(album): album for album in data.albums}

def save_data(id: int, data: Manager) -> None:
    album_data = [album.__dict__ for album in data.albums]

    with open(f"albums/{id}.json", "w") as file:
        json.dump(album_data, file, indent = 4)

# -- Testing -- #
if __name__ == "__main__":
    print()
    data: Manager = load_albums()
    print(data)