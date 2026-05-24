""" helper functions """

import os
from pathlib import Path
import pwd
import tomllib

import input_output

class UserOptions:
    def __init__(self, stuff):
        if stuff is not None:
            self.admin = stuff.get("admin", 0)
            self.rooms = stuff.get("rooms", dict())
        else:
            self.admin = 0
            self.rooms = dict()

    def note_room(self, name, max):
        self.rooms[name] = max

    def room_max(self, name):
        if name in self.rooms:
            return self.rooms[name]

        self.rooms[name] = 0
        return 0

    def to_dict(self):
        return {"admin": int(self.admin), "rooms": self.rooms}


def get_user() -> tuple:
    rc = pwd.getpwuid(os.getuid())
    return rc.pw_name, rc.pw_gecos


def normalize_room(room: str) -> str:
    return " ".join([k.capitalize() for k in room.split(" ") if len(k)])


def known_rooms(io, db, verbose: int, user_options, verbose_option: int):
    """
        this is weird but "verbose" is from the pyhenge command line and
        "verbose_option" is from the . command

        still to do:  add "*" after rooms with unread messages
        and do something useful with the verbose option flag
    """
    rooms = db.rooms()
    text = ""
    for room in rooms:
        new_messages = ""

        if room.get("max", 0) > user_options.room_max(room["name"]):
            new_messages = "*"

        text = text + room["name"] + ">" + new_messages + "\n"

    fmt = input_output.Formatter(io, False)
    fmt.format(text)


def num_with_plural(val: int, singular, plural) -> str:
    if val == 1:
        return f"{val} {singular}"

    return f"{val} {plural}"


def status(io, db, verbose: int, verbose_option: int):
    version = None
    p = Path('pyproject.toml')
    if p.exists():
        with open(str(p), 'rb') as f:
            v = tomllib.load(f)
            version = v["project"]["version"]

    if version is not None:
        io.put_string(f" pyhenge {version}")

    st = db.status()

    text = ""
    for k in [("message", "messages"), ("room", "rooms"), ("user", "users")]:
        if k[1] in st:
            v = num_with_plural(st[k[1]], k[0], k[1])
            text += f" {v}\n"

    fmt = input_output.Formatter(io, False)
    fmt.format(text)


def new_room(io, db, verbose: int):
    name = normalize_room(io.get_string("New Room: "))

    rc = db.new_room(name, dict())
    if rc == -1:
        io.put_string(f"Room '{name}' already exists")
        io.new_lines()
        return

