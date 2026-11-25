"""Small persistent store for workspace inquiries and synchronized UI state."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


class WorkspaceStateStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS inquiries (
                seq INTEGER PRIMARY KEY AUTOINCREMENT,
                engagement_id TEXT NOT NULL,
                request_id TEXT NOT NULL UNIQUE,
                payload TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS workspace_state (
                engagement_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                payload TEXT NOT NULL,
                PRIMARY KEY (engagement_id, user_id))""")

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.path)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    @staticmethod
    def _encode(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

    def add_inquiry(self, ticket):
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO inquiries (engagement_id, request_id, payload) VALUES (?, '', '{}')",
                (ticket["engagement_id"],))
            request_id = f"IRL_REQ_{cursor.lastrowid:04d}"
            saved = dict(ticket, request_id=request_id)
            db.execute("UPDATE inquiries SET request_id=?, payload=? WHERE seq=?",
                       (request_id, self._encode(saved), cursor.lastrowid))
        return saved

    def update_inquiry(self, ticket):
        with self._connect() as db:
            cursor = db.execute("UPDATE inquiries SET payload=? WHERE request_id=? AND engagement_id=?",
                                (self._encode(ticket), ticket["request_id"], ticket["engagement_id"]))
            if cursor.rowcount != 1:
                raise KeyError("Unknown inquiry: " + ticket["request_id"])

    def get_inquiry(self, engagement_id, request_id):
        with self._connect() as db:
            row = db.execute("SELECT payload FROM inquiries WHERE engagement_id=? AND request_id=?",
                             (engagement_id, request_id)).fetchone()
        return json.loads(row[0]) if row else None

    def all_inquiries(self):
        with self._connect() as db:
            rows = db.execute("SELECT payload FROM inquiries ORDER BY seq").fetchall()
        return [json.loads(row[0]) for row in rows]

    def save_state(self, engagement_id, user_id, state):
        with self._connect() as db:
            db.execute("""INSERT INTO workspace_state VALUES (?, ?, ?)
                ON CONFLICT(engagement_id, user_id) DO UPDATE SET payload=excluded.payload""",
                (engagement_id, user_id, self._encode(state)))

    def get_state(self, engagement_id, user_id):
        with self._connect() as db:
            row = db.execute("SELECT payload FROM workspace_state WHERE engagement_id=? AND user_id=?",
                             (engagement_id, user_id)).fetchone()
        return json.loads(row[0]) if row else None
