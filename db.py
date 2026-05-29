"""
    database functions
"""

import json
import sqlite3
from contextlib import contextmanager

from config import db_url


@contextmanager
def cursor_for(conn, do_commit=False):
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        if do_commit:
            conn.commit()

        cursor.close()


class DB:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.setup()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        self.conn.commit()

    def new(self):
        """ create tables if they don't exist"""
        with cursor_for(self.conn, do_commit=True) as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_name TEXT,
                    full_name TEXT,
                    options TEXT
                )
            """)
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_user_short_name ON users (short_name)
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    options TEXT
                )
            """)
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_room_name ON rooms (name)
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    headers TEXT,
                    body TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms_messages (
                    room_id INTEGER,
                    message_id INTEGER
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_room_id ON rooms_messages (room_id)
            """)
            try:
                cursor.execute("""
                    INSERT INTO rooms (room_id, name, options) VALUES (0, 'Lobby', '{}')
                """)
            except sqlite3.IntegrityError:
                """ this is okay """
                pass

    def setup(self):
        self.conn = sqlite3.connect(db_url)
        self.new()

    def close(self):
        self.conn.close()

    @staticmethod
    def from_json(j: str) -> dict:
        try:
            return json.loads(j)
        except TypeError:
            return {}

    @staticmethod
    def to_json(data: dict) -> str:
        return json.dumps(data)

    def get_user(self, user_id: int) -> dict|None:
        with cursor_for(self.conn) as cursor:
            cursor.execute("""
                SELECT user_id, short_name, full_name, options FROM users WHERE user_id = ?
            """, (user_id,))

            rc = cursor.fetchone()

            if rc is None:
                return None

            return dict(user_id=int(rc[0]), short_name=rc[1], full_name=rc[2], options=DB.from_json(rc[3]))

    def get_user_by_name(self, name: str) -> dict|None:
        with cursor_for(self.conn) as cursor:
            cursor.execute("""
                SELECT user_id, short_name, full_name, options FROM users WHERE short_name = ?
            """, (name,))

            rc = cursor.fetchone()

            if rc is None:
                return None

            return dict(user_id=rc[0], short_name=rc[1], full_name=rc[2], options=DB.from_json(rc[3]))

    def new_user(self, short_name: str, full_name: str, options: dict):
        with cursor_for(self.conn, do_commit=True) as cursor:
            try:
                cursor.execute("""
                INSERT INTO users (short_name, full_name, options) VALUES (?, ?, ?)
                """, (short_name, full_name, DB.to_json(options)))

                return cursor.lastrowid
            except sqlite3.IntegrityError:
                print(f"user {short_name} already exists???")
                return None

    def update_user_options(self, user_id: int, user_data: dict):
        with cursor_for(self.conn, do_commit=True) as cursor:
            try:
                cursor.execute("""
                    UPDATE users SET options = ? WHERE user_id = ?
                """, (DB.to_json(user_data), user_id))
            except sqlite3.IntegrityError:
                print(f"user {user_id} update failed???")

    def get_room(self, room_id: int) -> dict|None:
        with cursor_for(self.conn) as cursor:
            cursor.execute("""
                SELECT room_id, name, options FROM rooms WHERE room_id = ?
            """, (room_id,))

            rc = cursor.fetchone()

            if rc is None:
                return None

            return dict(room_id=int(rc[0]), name=rc[1], options=DB.from_json(rc[2]))

    def new_room(self, name: str, options: dict) -> int:
        with cursor_for(self.conn, do_commit=True) as cursor:
            try:
                cursor.execute("""
                    INSERT INTO rooms (name, options) VALUES (?, ?)
                """, (name, DB.to_json(options)))
            except sqlite3.IntegrityError:
                return -1

            return cursor.lastrowid

    def update_room_options(self, room_id: int, options: dict):
        with cursor_for(self.conn, do_commit=True) as cursor:
            cursor.execute("""
                UPDATE rooms SET options = ? WHERE room_id = ?
            """, (DB.to_json(options), room_id))

    def get_message(self, message_id: int) -> dict|None:
        with cursor_for(self.conn) as cursor:
            cursor.execute("""
                SELECT message_id, headers, body FROM messages WHERE message_id = ?
                """, (message_id,))

            rc = cursor.fetchone()

            if rc is None:
                return None

            return dict(message_id=int(rc[0]), headers=DB.from_json(rc[1]), body=rc[2])

    def new_message(self, body: str, headers: dict) -> int:
        with cursor_for(self.conn, do_commit=True) as cursor:
            cursor.execute("""
                INSERT INTO messages (body, headers) VALUES (?, ?)
            """, (body, DB.to_json(headers)))
            return cursor.lastrowid

    def note_message(self, message_id: int, room_id: int):
        with cursor_for(self.conn, do_commit=True) as cursor:
            cursor.execute("""
                INSERT INTO rooms_messages (room_id, message_id) VALUES (?, ?)
            """, (room_id, message_id))

    def newest_message(self, room_id: int) -> int:
        with cursor_for(self.conn) as cursor:
            cursor.execute("""
                SELECT MAX(message_id) FROM rooms_messages WHERE room_id = ?
            """, (room_id,))

            rc = cursor.fetchone()

        if rc is None:
            return 0

        return int(rc[0])

    def rooms(self) -> list[dict]:
        all_rooms = self.rooms_as_dict()

        rc = list()
        for k in sorted(all_rooms.keys(), key=lambda r : all_rooms[r]["room_id"]):
            v = all_rooms[k]
            rc.append(v)

        return rc

    def rooms_as_dict(self) -> dict:
        with cursor_for(self.conn) as cursor:
            cursor.execute("""
                SELECT room_id, name FROM rooms ORDER BY room_id ASC
            """)
            rows = cursor.fetchall()

            all_rooms = {r[1]: dict(name=r[1], room_id=int(r[0]), max=0) for r in rows}

            cursor.execute("""
                SELECT rooms.name, MAX(rooms_messages.message_id) FROM rooms, rooms_messages WHERE rooms.room_id = rooms_messages.room_id GROUP BY rooms_messages.room_id ORDER BY rooms_messages.room_id ASC
            """)

            rows = cursor.fetchall()

        if rows is not None:
            for r in rows:
                all_rooms[r[0]]["max"] = int(r[1])

        return all_rooms

    def users(self) -> list[dict]:
        with cursor_for(self.conn) as cursor:
            cursor.execute("""
                SELECT full_name FROM users
            """)

            rows = cursor.fetchall()

        if rows is None:
            return list()

        return [dict(full_nane=r[0]) for r in rows]

    def status(self) -> dict:
        rc = dict()

        slots = [
            ("messages", "messages"),
            ("rooms", "rooms"),
            ("users", "users"),
        ]

        with cursor_for(self.conn) as cursor:
            for s in slots:
                cursor.execute(f"SELECT COUNT(*) FROM {s[0]}")
                rc[s[1]] = cursor.fetchone()[0]

        return rc

    def messages_in_room(self, room_id: int) -> list[int]:
        with cursor_for(self.conn) as cursor:
            cursor.execute(
                """
                SELECT message_id FROM rooms_messages WHERE room_id = ? ORDER BY message_id ASC
                """, (room_id,)
            )

            rows = cursor.fetchall()
        return [int(r[0]) for r in rows]

