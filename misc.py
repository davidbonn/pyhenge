""" helper functions """

import os
import pwd

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

        print(f" ---- setting self.rooms[{name}] to 0")
        self.rooms[name] = 0
        return 0

    def to_dict(self):
        return {"admin": int(self.admin), "rooms": self.rooms}


def get_user() -> tuple:
    rc = pwd.getpwuid(os.getuid())
    return rc.pw_name, rc.pw_gecos


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
    st = db.status()

    text = ""
    for k in [("message", "messages"), ("room", "rooms"), ("user", "users")]:
        if k[1] in st:
            v = num_with_plural(st[k[1]], k[0], k[1])
            text += f" {v}\n"

    fmt = input_output.Formatter(io, False)
    fmt.format(text)


def new_room(io, db, verbose: int):
    all_rooms = db.rooms_as_dict()
    name = io.get_string("New Room: ")

    if name in all_rooms:
        io.put_string(f"Room '{name}' already exists")
        io.new_lines()
        return

    db.new_room(name, dict())
