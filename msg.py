"""
    message text editor
    helpers to print message header
    helpers to print a message
"""

import time

import help
from input_output import Formatter
import misc
from command import CommandsAndOptions


def create_message(io) -> str:
    buffer = ""

    def edit_menu(to_edit: str) -> tuple[str, str]:
        while True:
            io.put_string("Edit command: ")
            ch = io.get_char().upper()

            match ch:
                case '?':
                    io.put_string("Help")
                    help.show_help(io, "edit-menu",)
                    io.new_lines()
                case 'Q':
                    io.put_string("Quit")
                    io.new_lines()
                    return "", "quit"
                case 'S':
                    io.put_string("Save")
                    io.new_lines()
                    return to_edit, "save"
                case 'C':
                    io.put_string("Continue")
                    io.new_lines()
                    return to_edit, "continue"
                case 'R':
                    io.put_string("Replace")
                    io.new_lines()
                    find = io.get_string("Find: ")
                    replace = io.get_string("Replace: ")
                    to_edit = to_edit.replace(find, replace, 1)
                    io.new_lines()
                case 'P':
                    io.put_string("Print")
                    io.new_lines()
                    fmt = Formatter(io, False)
                    fmt.format(to_edit)
                    io.new_lines()
                case _:
                    io.put_string("\a")

    while True:
        ch = io.get_char()

        if ch == '\r' or ch == '\n':
            io.new_lines()

            if len(buffer) > 0 and buffer[-1] == '\n':
                buffer, rc = edit_menu(buffer)

                if rc == 'quit':
                    return ""
                elif rc == 'save':
                    return buffer
            else:
                buffer += '\n'
        elif ch == '\b' or ord(ch) == 127:
            buffer = buffer[0:-1]
            io.put_string('\b \b')
        else:
            io.put_string(ch)
            buffer += ch


def header(hdr):
    rc = ""

    if "When" in hdr:
        when = time.strftime("%a %d%b %H:%M", time.localtime(hdr["When"]))
        rc += f" {when} "

    if "Author" in hdr:
        author = hdr["Author"]
        rc += f"From {author} "
    else:
        rc += f"From An Anonymous Coward "

    if len(rc) > 0:
        rc += "\n"

    return rc


def count_messages(message_ids, newest):
    total_messages = len(message_ids)
    new_messages = len([msg_id for msg_id in message_ids if msg_id > newest])
    total_messages = misc.num_with_plural(total_messages, "message", "messages")

    if new_messages > 0:
        new_messages = f" {new_messages} new"
        return f" {total_messages}\n {new_messages}\n "

    return f" {total_messages}\n "


def show_messages(io, db, message_ids, newest, how, verbose):
    def show_message(h, body):
        my_text = f" {header(h)} {body}\n"
        fmt = Formatter(io, True)
        return fmt.format(my_text)

    if verbose:
        io.put_string("P)ause N)ext S)top")
        io.new_lines()

    match how:
        case CommandsAndOptions.REVERSE:
            for m in reversed(message_ids):
                src = db.get_message(m)
                if src is not None:
                    rc = show_message(src["headers"], src["body"])
                    if rc == 'S':
                        break

        case CommandsAndOptions.FORWARD:
            for m in message_ids:
                src = db.get_message(m)
                if src is not None:
                    rc = show_message(src["headers"], src["body"])
                    if rc == 'S':
                        break

        case CommandsAndOptions.NEW:
            for m in message_ids:
                src = db.get_message(m)
                if src is not None and src["message_id"] > newest:
                    rc = show_message(src["headers"], src["body"])
                    if rc == 'S':
                        break

