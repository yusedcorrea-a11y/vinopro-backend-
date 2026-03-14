"""
SQLite para usuarios registrados (email/social) y sesiones.
Ruta: data/vino_pro.db
"""
import sqlite3
import uuid
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "vino_pro.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def init_db():
    """Crea tablas users y sessions si no existen."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE,
                password_hash TEXT,
                google_id TEXT UNIQUE,
                facebook_id TEXT UNIQUE,
                avatar_path TEXT DEFAULT '',
                display_name TEXT DEFAULT '',
                created_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_users_google ON users(google_id);
            CREATE INDEX IF NOT EXISTS idx_users_facebook ON users(facebook_id);

            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
        """)
        conn.commit()
    finally:
        conn.close()


def create_user(email: str | None, password_hash: str | None, google_id: str | None = None, facebook_id: str | None = None, avatar_path: str = "", display_name: str = "") -> int | None:
    """Crea usuario. Devuelve user_id o None si falla (ej. email duplicado)."""
    import time
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO users (email, password_hash, google_id, facebook_id, avatar_path, display_name, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (email or None, password_hash or None, google_id or None, facebook_id or None, avatar_path or "", display_name or "", int(time.time())),
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_email(email: str) -> dict | None:
    """Devuelve fila user por email o None."""
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id, email, password_hash, avatar_path, display_name, created_at FROM users WHERE email = ?", (email.strip().lower(),))
        row = cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "email": row[1], "password_hash": row[2], "avatar_path": row[3] or "", "display_name": row[4] or "", "created_at": row[5]}
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> dict | None:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT id, email, avatar_path, display_name FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return None
        return {"id": row[0], "email": row[1], "avatar_path": row[2] or "", "display_name": row[3] or ""}
    finally:
        conn.close()


def create_session(user_id: int) -> str:
    """Crea una sesión para user_id. Devuelve session_id."""
    import time
    session_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        conn.execute("INSERT INTO sessions (session_id, user_id, created_at) VALUES (?, ?, ?)", (session_id, user_id, int(time.time())))
        conn.commit()
        return session_id
    finally:
        conn.close()


def get_user_id_by_session(session_id: str) -> int | None:
    """Devuelve user_id asociado a session_id o None."""
    if not (session_id or "").strip():
        return None
    conn = get_connection()
    try:
        cur = conn.execute("SELECT user_id FROM sessions WHERE session_id = ?", (session_id.strip(),))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def update_user_avatar(user_id: int, avatar_path: str) -> bool:
    conn = get_connection()
    try:
        conn.execute("UPDATE users SET avatar_path = ? WHERE id = ?", (avatar_path, user_id))
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()
