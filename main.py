#!/usr/bin/env uv run main.py

import argparse
from pathlib import Path
import signal
import time

import config
from db import DB
from input_output import InputOutput, Formatter
from command import Command, CommandsAndOptions
import help
import misc
import msg

debug = True

class AbortException(Exception):
    pass


class App:
    def __init__(self, verbose, baud_rate):
        self.db = None
        self.io = None
        self.command = None
        self.verbose = verbose
        self.baud_rate = baud_rate

        self.current_room = None
        self.messages = None
        self.user_id = None
        self.user = None
        self.full_name = None
        self.user_options = None

    @staticmethod
    def handler(signum, frame):
        raise AbortException()

    def setup_user(self):
        self.user, self.full_name = misc.get_user()

        if debug:
            print(f"User name: {self.user}")
            print(f"Full name: {self.full_name}")

        u = self.db.get_user_by_name(self.user)

        if u is None:
            if debug:
                print(f"User {self.user} not present, adding it to database")

            null_dict = dict(admin=0,rooms=dict())
            new_id = self.db.new_user(self.user, self.full_name, null_dict)
            if debug:
                print(f"New user ID: {new_id}")

            """ eventually add check if we are the first user (id==1) to set admin=1 in user_options """

            self.user_id = new_id
            self.user_options = misc.UserOptions(null_dict)
        else:
            if debug:
                print(f"User {self.user} present, setting up")

            self.user_id = int(u.get("user_id"))
            self.user_options = misc.UserOptions(u.get("options", None))

    def save_user(self):
        self.db.update_user_options(self.user_id, self.user_options.to_dict())

    def note_current_room(self):
        if self.current_room is not None:
            if self.messages is None or len(self.messages) == 0:
                max_val = 0
            else:
                max_val = max(self.messages)

            self.user_options.note_room(self.current_room["name"], max_val)
            self.save_user()

    def goto_next_room(self):
        """
            there is an ugly inefficiency here where we basically do the identical
            database queries twice, once here with self.db.rooms() and in self.goto_room()
            with self.db.rooms_as_dict().
        """
        rooms = self.db.rooms()

        if self.current_room is None:
            self.io.put_string('--> No current room?')
            self.io.new_lines()
            return

        """
            this code block is also a lot unPythonic and contrived and 
            needs a rethink
        """

        # find the current room in the rooms list
        i = 0
        while i < len(rooms):
            if rooms[i]['name'] == self.current_room["name"]:
                break
            i += 1

        # if we aren't at the end of the rooms list, find the next room (if any)
        # with unread messages
        if i < len(rooms):
            i += 1

            while i < len(rooms):
                if rooms[i].get("max", 0) > self.user_options.room_max(rooms[i]["name"]):
                    break

                i += 1

        # if we are at the end of the rooms list, go back to the first room
        # otherwise go to the room we are pointed at
        if i == len(rooms):
            nm = rooms[0]['name']
        else:
            nm = rooms[i]['name']

        self.io.put_string(f"---> {nm}")
        self.io.new_lines()
        self.goto_room(nm)

    def goto_room(self, room):
        all_rooms = self.db.rooms_as_dict()

        if room not in all_rooms:
            self.io.put_string(f"No room {room}")
            return

        self.note_current_room()
        self.current_room = all_rooms[room]
        self.update_messages()

        fmt = Formatter(self.io, False)
        fmt.format(msg.count_messages(self.messages, self.user_options.room_max(self.current_room["name"])))

    def update_messages(self):
        if self.current_room is None:
            self.messages = list()

        self.messages = self.db.messages_in_room(self.current_room["room_id"])

    def show_config(self):
        text = f"""
            User ID: {self.user_id}
            User name: {self.user}
            Full name: {self.full_name}
        """

        fmt = Formatter(self.io, False)
        fmt.format(text)

    def process_command(self, command):
        match command:
            case [CommandsAndOptions.LOGOUT]:
                return True
            case [CommandsAndOptions.HELP,fn]:
                if fn is None:
                    fn = self.io.get_string('')

                self.io.new_lines()
                help.show_help(self.io, fn, self.verbose)
            case [CommandsAndOptions.READ, direction, *options]:
                self.io.new_lines()
                verbose = len(options)
                msg.show_messages(
                    self.io, self.db, self.messages,
                    self.user_options.room_max(self.current_room["name"]),
                    direction, self.verbose
                )
            case [CommandsAndOptions.ENTER, CommandsAndOptions.MESSAGE]:
                self.io.new_lines()
                message = msg.create_message(self.io)

                if message == "":
                    self.io.put_string('Abandoned!')
                else:
                    if debug:
                        self.io.put_string('Saving message')

                    headers = dict()
                    headers["Author"] = self.full_name
                    headers["When"] = round(time.time())

                    new_id = self.db.new_message(message, headers)

                    if self.current_room is not None:
                        self.db.note_message(new_id, self.current_room["room_id"])

                    self.update_messages()
            case [CommandsAndOptions.GOTO, room]:
                if room is None:
                    """ a good place for tab completion """
                    room = misc.normalize_room(self.io.get_string(''))
                    self.goto_room(room)
                else:
                    self.goto_next_room()
            case [CommandsAndOptions.SHOW, CommandsAndOptions.ROOMS, *options]:
                self.io.new_lines()
                verbose = len(options)
                misc.known_rooms(self.io, self.db, self.verbose, self.user_options, verbose)
            case [CommandsAndOptions.SHOW, CommandsAndOptions.STATUS, *options]:
                self.io.new_lines()
                verbose = len(options)
                misc.status(self.io, self.db, self.verbose, verbose)
            case [CommandsAndOptions.SHOW, CommandsAndOptions.CONFIGURATION, *options]:
                self.io.new_lines()
                verbose = len(options)
                self.show_config()
            case [CommandsAndOptions.ENTER, CommandsAndOptions.ROOM]:
                self.io.new_lines()
                misc.new_room(self.io, self.db, self.verbose)
            case _ :
                self.io.put_string(f"Invalid command: '{command=}'")

        return False

    def prompt(self):
        if self.current_room is None:
            self.io.put_string('No Room?>>>> ')
        else:
            self.io.put_string(f"{self.current_room['name']}> ")

    def mainloop(self):
        self.db = DB()
        self.io = InputOutput(self.baud_rate)
        self.command = Command(self.io)
        signal.signal(signal.SIGTERM, App.handler)

        try:
            fn = Path(config.db_url)
            fn.chmod(0o666)
        except OSError as e:
            pass

        with self.db:
            self.setup_user()
            help.show_help(self.io, "intro", False)
            self.io.new_lines()
            self.goto_room("Lobby")

            with self.io:
                try:
                    while True:
                        self.prompt()
                        cmd = self.command.get()
                        quit = self.process_command(cmd)
                        self.io.new_lines()

                        if quit:
                            self.io.put_string("Logging out")
                            self.io.new_lines()
                            self.save_user()
                            break
                except AbortException:
                    self.io.new_lines()
                    self.io.put_string("Aborting")
                    self.io.new_lines()
                    return


def main():
    print("Hello from pyhenge!")

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true",)
    ap.add_argument("-b", "--baud_rate", type=int, default=1200)

    args = ap.parse_args()

    App(args.verbose,args.baud_rate).mainloop()


if __name__ == "__main__":
    main()
