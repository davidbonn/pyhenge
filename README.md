## What this is about

This is an attempt to make a Stonehenge clone implemented in Python.

## Assumptions

1.  Use a back-end database (sqlite3) for storage rather than files so we can run multiple users.
2.  Linux users map to users of pyhenge.  We keep a per-user record (although storing that info in a dot file also would work).
3.  Text mode only.  Render messages using traditional Citadel conventions.

## Stuff We Do Not Have

1. Networking
2. Admin functions
3. Groups, Hallways, Doors
4. Directory Rooms
5. Hidden Rooms
6. No private mail
7. No provision for expiring old messages
8. Some obscure advanced commands do not work

## Things to think about and fix

1. Database needs to have more keys defined for efficient searching and to maintain uniqueness constraints.
2. Case-sensitive room names.  And a race condition with creating new rooms.
3. Rendering causes excessive blank lines in some cases and not enough blank lines in other cases.
4. Need to test multi-user.
5. Clean up some of the uglier code.  Particularly about how unread messages are tracked by the user record.
6. Catch SIGTERM and clean up terminal settings and database on the way out.
7. Won't work smoothly if the same user is running two instances of pyhenge.
8. Verbose options on .Read and .Show do nothing at the moment.


