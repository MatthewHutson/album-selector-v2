# -- Imports -- #
from classes import *
from random import choice

# -- Functions -- #
def first(data: Manager, num: int) -> dict[str, list[Album]]:
    '''Filters the first [num] albums in each category orderd by number of listens'''
    categories = {
        "short": sorted(data.short, key = lambda a: a.listen_count),
        "medium": sorted(data.medium, key = lambda a: a.listen_count),
        "long": sorted(data.long, key = lambda a: a.listen_count)
    }

    for category, albums in categories.items():
        categories[category] = albums[:num]

    return categories

def selction(data: Manager, num: int = 3) -> list[Album]:
    '''Selects a random album from the filtered albums'''
    possibilities: dict = first(data, num)

    short = possibilities["short"]
    medium = possibilities["medium"]
    long = possibilities["long"]

    nested_albums: list[list[Album]] = [short, medium, long]
    out: list[Album] = []

    for category in nested_albums:
        if len(category) != 0:
            out.append(choice(category))
    
    return out

def output_selection(data: Manager) -> Manager:
    '''Outputs the selection from the manager'''
    albums = selction(data)
    out_manager = Manager(albums)

    return out_manager

# -- Testing -- #
if __name__ == "__main__":
    albums = []

    for i in range(20):
        temp = Album(str(i), "test", 10 * i, i)
        albums.append(temp)

    data = Manager(albums)

    print()
    print(first(data, 5))
    print()
    print(selction(data))
    print()
    print(str(output_selection(data)))