"""
    input and output functions
    and formatted output functions
"""

import os
import select
import sys
import tty
import termios
import time


class InputOutput:
    def __init__(self, baud_rate=19200):
        self.baud_rate = baud_rate
        self.width = os.get_terminal_size().columns
        self.fd = sys.stdin.fileno()
        self.old_settings = termios.tcgetattr(self.fd)

    def __enter__(self):
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)

    def __exit__(self, exc_type, exc_val, exc_tb):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)

    def beep(self):
        self.put_string("\a")

    def get_terminal_width(self) -> int:
        return self.width

    def char_ready(self) -> bool:
        ready, _, _ = select.select([self.fd], [], [], 0.0001)
        return bool(ready)

    def get_char(self) -> str:
        ch = os.read(self.fd, 1)
        return ch.decode('ascii')

    def put_string(self, string: str):
        if self.baud_rate >= 2400:
            sys.stdout.write(string)
            sys.stdout.flush()
            time.sleep(len(string) / (self.baud_rate // 10))
        else:
            sleep_time = 10 / self.baud_rate
            for char in string:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(sleep_time)

    def get_yes_no(self, prompt: str) -> bool:
        if len(prompt):
            self.put_string(prompt)

        while True:
            ch = self.get_char()

            if ch == 'y' or ch == 'Y':
                return True
            elif ch == 'n' or ch == 'N':
                return False

            self.beep()

    def get_string(self, prompt: str) -> str:
        if len(prompt):
            self.put_string(prompt)

        rc = ""
        while True:
            ch = self.get_char()

            if ch == '\r' or ch == '\n':
                self.new_lines()
                return rc

            if ch == '\b' or ord(ch) == 127:
                rc = rc[0:-1]
                self.put_string('\b \b')
                continue

            if ord(ch) < 32 or ord(ch) > 126:
                self.put_string('\a')
                continue

            self.put_string(ch)
            rc += ch

        return ""

    def new_lines(self, count=1):
        self.put_string('\r\n' * count)


class FormatException(Exception):
    def __init__(self, flavor):
        self.flavor = flavor


"""
    format text using CrT style conventions, namely:
     1.  blank lines end paragraphs
     2.  indented lines end paragraphs
     3.  (S)top (P)ause (N)ext, (N)ext is optional
"""
class Formatter:
    def __init__(self, io, use_next):
        self.io = io
        self.use_next = use_next
        self.pos = 0

    def end_line(self, count = 1):
        self.io.put_string('\r\n' * count)
        self.pos = 0

        if self.io.char_ready():
            ch = self.io.get_char().upper()

            match ch:
                case 'P':
                    _ = self.io.get_char()

                case 'N':
                    if self.use_next:
                        raise FormatException('N')

                case 'S':
                    raise FormatException('S')

    def format(self, text: str) -> str:
        width = self.io.get_terminal_width()
        lines = text.splitlines()
        leading_lines = True

        self.pos = 0

        try:
            for line in lines:
                # skeezy hack to eliminate blank leading lines
                if leading_lines:
                    if len(line):
                        leading_lines = False
                    else:
                        continue

                if len(line) == 0:
                    self.end_line()
                elif line[0].isspace():
                    self.end_line()

                words = line.split()

                for word in words:
                    if len(word) >= width:
                        if self.pos > 0:
                            self.end_line()

                        self.io.put_string(word)
                        self.end_line()
                    elif self.pos + len(word) >= width:
                        self.end_line()
                        self.io.put_string(word)
                        self.pos += len(word)
                    else:
                        self.io.put_string(' ')
                        self.io.put_string(word)
                        self.pos += len(word) + 1

        except FormatException as e:
            return e.flavor

        return '0'



