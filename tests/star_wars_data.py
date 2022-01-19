"""This defines a basic set of data for our Star Wars Schema.

This data is hard coded for the sake of the demo, but you could imagine
fetching this data from a backend service rather than from hardcoded
JSON objects in a more complex demo.
"""

from typing import List, NamedTuple, Optional


class Ship(NamedTuple):
    id: str
    name: str


all_ships = [
    Ship("1", "X-Wing"),
    Ship("2", "Y-Wing"),
    Ship("3", "A-Wing"),
    # Yeah, technically it's Corellian. But it flew in the service of the rebels,
    # so for the purposes of this demo it's a rebel ship.
    Ship("4", "Millennium Falcon"),
    Ship("5", "Home One"),
    Ship("6", "TIE Fighter"),
    Ship("7", "TIE Interceptor"),
    Ship("8", "Executor"),
]


class Faction(NamedTuple):
    id: str
    name: str
    ships: List[str]


rebels = Faction("1", "Alliance to Restore the Republic", ["1", "2", "3", "4", "5"])

empire = Faction("2", "Galactic Empire", ["6", "7", "8"])

all_factions = [rebels, empire]


def create_ship(ship_name: str, faction_id: str) -> Ship:
    new_ship = Ship(str(len(all_ships) + 1), ship_name)
    all_ships.append(new_ship)
    faction = get_faction(faction_id)
    if faction:
        faction.ships.append(new_ship.id)
    return new_ship


def get_ship(id_: str) -> Optional[Ship]:
    return next(filter(lambda ship: ship.id == id_, all_ships), None)  # type: ignore


def get_faction(id_: str) -> Optional[Faction]:
    return next(
        filter(lambda faction: faction.id == id_, all_factions), None  # type: ignore
    )


def get_rebels() -> Faction:
    return rebels


def get_empire() -> Faction:
    return empire
