"""
    parses commands, also help text lives here
"""

import enum

class CommandsAndOptions(enum.StrEnum):
    HELP = enum.auto()
    LOGOUT = enum.auto()
    ENTER = enum.auto()
    READ = enum.auto()
    SHOW = enum.auto()
    GOTO = enum.auto()

    REVERSE = enum.auto()
    NEW = enum.auto()
    FORWARD = enum.auto()

    MESSAGE = enum.auto()
    CONFIGURATION = enum.auto()

    STATUS = enum.auto()
    USERS = enum.auto()

    NEXT_ROOM = enum.auto()
    ROOMS = enum.auto()
    ROOM = enum.auto()

    VERBOSE = enum.auto()


class Command:
    def __init__(self, io):
        self.io = io
        self.command = list()

        self.control_c = chr(3)
        self.control_d = chr(4)

    def get(self) -> list:
        ch = self.io.get_char().upper()
        self.command = list()

        match ch:
            case '?':
                # help
                self.io.put_string('Help')
                self.command = [CommandsAndOptions.HELP, "main-menu"]
            case 'L' | self.control_c | self.control_d :
                self.io.put_string('Logout ')
                self.command = [CommandsAndOptions.LOGOUT]
            case 'G':
                self.io.put_string('Goto ')
                self.command = [CommandsAndOptions.GOTO, CommandsAndOptions.NEXT_ROOM]
            case 'E':
                self.io.put_string('Enter Message')
                self.command = [CommandsAndOptions.ENTER, CommandsAndOptions.MESSAGE]
            case 'F':
                self.io.put_string('Read Forward')
                self.command = [CommandsAndOptions.READ, CommandsAndOptions.FORWARD]
            case 'R':
                self.io.put_string('Read Reverse')
                self.command = [CommandsAndOptions.READ, CommandsAndOptions.REVERSE]
            case 'N':
                self.io.put_string('Read New')
                self.command = [CommandsAndOptions.READ  ,CommandsAndOptions.NEW]
            case 'K':
                self.io.put_string('Known Rooms')
                self.command = [CommandsAndOptions.SHOW, CommandsAndOptions.ROOMS]
            case 'H':
                self.io.put_string('Help')
                self.command = [CommandsAndOptions.HELP, "general"]
            case '.':
                # extended dot command
                self.io.put_string('.')
                self.extended_command()
            case _:
                self.io.put_string('\a')

        return self.command

    def extended_command(self):
        ch = self.io.get_char().upper()

        match ch:
            case 'R':
                self.io.put_string('Read ')
                self.read_command()
            case 'H':
                self.io.put_string('Help ')
                self.command = [CommandsAndOptions.HELP, None]
            case 'S':
                self.io.put_string('Show ')
                self.show_command()
            case 'E':
                self.io.put_string('Enter ')
                self.enter_command()
            case 'G':
                self.io.put_string('Goto ')
                self.command = [CommandsAndOptions.GOTO, None]
            case '?':
                self.io.put_string('Help')
                self.command = [CommandsAndOptions.HELP, "dot-menu"]
            case _:
                self.io.put_string('\a')

    def read_command(self):
        verbose = False

        while len(self.command) == 0:
            ch = self.io.get_char().upper()

            match ch:
                case 'R':
                    self.io.put_string('Reverse ')
                    self.command = [CommandsAndOptions.READ, CommandsAndOptions.REVERSE]
                case 'F':
                    self.io.put_string('Forward ')
                    self.command = [CommandsAndOptions.READ, CommandsAndOptions.FORWARD]
                case 'N':
                    self.io.put_string('New ')
                    self.command = [CommandsAndOptions.READ, CommandsAndOptions.NEW]
                case 'V':
                    self.io.put_string('Verbose ')
                    verbose = True
                case '?':
                    self.io.put_string('Help')
                    self.command = [CommandsAndOptions.HELP, 'read-menu']
                case _:
                    self.io.put_string('\a')

        if verbose:
            self.command.append(CommandsAndOptions.VERBOSE)

    def show_command(self):
        verbose = False

        while len(self.command) == 0:
            ch = self.io.get_char().upper()

            match ch:
                case 'R':
                    self.io.put_string('Rooms')
                    self.command = [CommandsAndOptions.SHOW, CommandsAndOptions.ROOMS]
                case 'C':
                    self.io.put_string('Configuration')
                    self.command = [CommandsAndOptions.SHOW, CommandsAndOptions.CONFIGURATION]
                case 'S':
                    self.io.put_string('Status')
                    self.command = [CommandsAndOptions.SHOW, CommandsAndOptions.STATUS]
                case 'U':
                    self.io.put_string('Users')
                    self.command = [CommandsAndOptions.SHOW, CommandsAndOptions.USERS]
                case 'V':
                    self.io.put_string('Verbose ')
                    verbose = True
                case '?':
                    self.io.put_string('Help')
                    self.command = [CommandsAndOptions.HELP, 'show-menu']
                case _:
                    self.io.put_string('\a')

        if verbose:
            self.command.append(CommandsAndOptions.VERBOSE)

    def enter_command(self):
        while len(self.command) == 0:
            ch = self.io.get_char().upper()

            match ch:
                case 'M':
                    self.io.put_string('Message')
                    self.command = [CommandsAndOptions.ENTER, CommandsAndOptions.MESSAGE]
                case 'R':
                    self.io.put_string('Room')
                    self.command = [CommandsAndOptions.ENTER, CommandsAndOptions.ROOM]
                case '?':
                    self.io.put_string('Help')
                    self.command = [CommandsAndOptions.HELP, 'enter-menu']
                case '_':
                    self.io.put_string('\a')
