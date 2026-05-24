"""
    where help text and menu functions live
"""

from input_output import Formatter


def show_help(io, text_id, verbose=False):
    if text_id not in help_text:
        io.put_string(f"Help for {text_id} not found!")
        return

    fmt = Formatter(io, False)

    text = help_text[text_id]
    if verbose:
        text = "P)ause S)top\n" + text

    fmt.format(text)


help_text = {
    "intro":
"""
Stonehenge, where the demons dwell
where the banshees live and they do live well.

Stonehenge, where a man is a man
and the children dance to the pipes of Pan.
""",
    "general":
"""
This is a Stonehenge-like BBS implemented in python.
It supports a somewhat broken subset of old Stonehenge features.

Stuff we don't yet do:
 1. No admin features, so no deleting or moving messages or renaming rooms.
 2. No provision for expiring old messages.
 3. No networking.
 4. No groups, hallways, doors.
 5. No private mail.
 6. Some advanced commands, (like Read New Reverse) aren't supported.
 
How to use it:
 Basic commands are single letters, use ? to get a menu.
 More advanced commands work by entering a "," and a command.
e.g. ".R" will access the Read commands used to read messages.  You can use "." commands
with ".R", ".S" (Show), and ".E" (Enter).  You can use a "?" to get a menu for each of these.
 
In addition, ".G" will let you enter a room name and Go To that room, and ".H" will let you
enter a Help topic and display that topic.

Room names are case sensitive and that is a bad thing.
""",
    "main-menu":
"""
 L)ogout
 G)oto
 K)nown Rooms
 E)nter Messages
 N)ew Read
 R)everse Read
 F)orward Read
 H)elp
 ?) this menu
""",
    "read-menu":
"""
 R)everse
 F)orward
 N)ew
 V)erbose (optional)
 ?) this menu
""",
    "enter-menu":
"""
 M)essage
 R)oom
 ?) this menu
""",
    "show-menu":
"""
 R)ooms
 C)onfiguration
 S)tatus
 U)sers
 V)erbose (optional)
 ?) this menu
""",
    "dot-menu":
"""
 R)ead
 E)nter
 S)how
 H)elp
 G)oto
 ?) this menu
""",
    "edit-menu":
"""
 C)ontinue editing
 P)rint text
 Q)uit without saving
 R)eplace text
 S)ave message
 ?) this menu
"""
}