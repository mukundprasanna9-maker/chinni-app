import os
import re
import socket
import sqlite3
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "chinni_db")
OFFLINE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chinni_offline.db")

_MYSQL_AVAILABLE = None


def get_db_config(include_db: bool = True) -> dict:
    config = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "password": DB_PASSWORD,
    }
    if include_db:
        config["database"] = DB_NAME
    return config


class SQLiteDictCursor:
    """Wrapper around SQLite cursor to emulate mysql.connector dictionary cursor."""

    def __init__(self, cursor, dictionary=False):
        self._cursor = cursor
        self.dictionary = dictionary
        self.lastrowid = None
        self.rowcount = -1

    def execute(self, query, params=None):
        sqlite_query = query.replace("%s", "?")
        if params is None:
            res = self._cursor.execute(sqlite_query)
        else:
            res = self._cursor.execute(sqlite_query, params)
        self.lastrowid = self._cursor.lastrowid
        self.rowcount = self._cursor.rowcount
        return res

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        if self.dictionary:
            cols = [col[0] for col in self._cursor.description]
            return dict(zip(cols, row))
        return row

    def fetchall(self):
        rows = self._cursor.fetchall()
        if not rows:
            return []
        if self.dictionary:
            cols = [col[0] for col in self._cursor.description]
            return [dict(zip(cols, r)) for r in rows]
        return rows

    def close(self):
        self._cursor.close()


class SQLiteConnectionWrapper:
    """Wrapper around SQLite connection to emulate mysql.connector connection."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self, dictionary=False):
        return SQLiteDictCursor(self._conn.cursor(), dictionary=dictionary)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def is_mysql_online() -> bool:
    global _MYSQL_AVAILABLE
    if _MYSQL_AVAILABLE is not None:
        return _MYSQL_AVAILABLE
    try:
        s = socket.socket()
        s.settimeout(0.3)
        res = s.connect_ex((DB_HOST, DB_PORT))
        s.close()
        if res != 0:
            _MYSQL_AVAILABLE = False
            return False

        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connection_timeout=1,
        )
        conn.close()
        _MYSQL_AVAILABLE = True
        return True
    except Exception:
        _MYSQL_AVAILABLE = False
        return False


def get_connection(include_db: bool = True):
    if is_mysql_online():
        config = get_db_config(include_db=include_db)
        return mysql.connector.connect(**config)
    else:
        conn = sqlite3.connect(OFFLINE_DB_PATH, timeout=10.0)
        conn.execute("PRAGMA foreign_keys = ON;")
        return SQLiteConnectionWrapper(conn)


SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        target_score INT DEFAULT 235,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS tracks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        target_score INT NOT NULL,
        max_score INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        track_id INT NOT NULL,
        name VARCHAR(100) NOT NULL,
        code VARCHAR(20) NOT NULL,
        max_marks INT NOT NULL,
        target_marks INT DEFAULT 0,
        FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS subject_groups (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subject_id INT NOT NULL,
        group_code VARCHAR(20) NOT NULL,
        name VARCHAR(150) NOT NULL,
        description TEXT,
        weight_percentage FLOAT DEFAULT 0.0,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS tests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        track_id INT NOT NULL,
        test_code VARCHAR(50) NOT NULL,
        test_type VARCHAR(30) DEFAULT 'FULL',
        test_date DATE NOT NULL,
        total_score FLOAT NOT NULL,
        max_score FLOAT NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS test_subject_scores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        test_id INT NOT NULL,
        subject_id INT NOT NULL,
        score FLOAT NOT NULL,
        max_score FLOAT NOT NULL,
        accuracy_percent FLOAT DEFAULT 0.0,
        time_spent_minutes INT DEFAULT 0,
        FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS test_group_scores (
        id INT AUTO_INCREMENT PRIMARY KEY,
        test_id INT NOT NULL,
        group_id INT NOT NULL,
        score FLOAT NOT NULL,
        max_score FLOAT NOT NULL,
        FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
        FOREIGN KEY (group_id) REFERENCES subject_groups(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS study_plans (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        group_id INT,
        subject_id INT,
        target_date DATE NOT NULL,
        planned_hours FLOAT NOT NULL,
        actual_hours FLOAT DEFAULT 0.0,
        notes TEXT,
        status VARCHAR(30) DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (group_id) REFERENCES subject_groups(id) ON DELETE SET NULL,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS focus_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        subject_id INT,
        group_id INT,
        duration_minutes INT NOT NULL,
        adherence_status VARCHAR(50) DEFAULT 'COMPLETED',
        notes TEXT,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE SET NULL,
        FOREIGN KEY (group_id) REFERENCES subject_groups(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]


def init_db():
    """Initializes the database and creates all tables."""
    if is_mysql_online():
        print(f"[Database] Using live MySQL Server at {DB_HOST}:{DB_PORT}")
        server_conn = get_connection(include_db=False)
        cursor = server_conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
        cursor.close()
        server_conn.close()

        db_conn = get_connection(include_db=True)
        cursor = db_conn.cursor()
        for stmt in SCHEMA_SQL:
            cursor.execute(stmt)
        db_conn.commit()
        cursor.close()
        db_conn.close()
    else:
        print(f"[Database] MySQL not reachable at {DB_HOST}:{DB_PORT}. Using local offline storage ({OFFLINE_DB_PATH}) for development/testing.")
        raw_conn = sqlite3.connect(OFFLINE_DB_PATH)
        raw_conn.execute("PRAGMA foreign_keys = ON;")
        for stmt in SCHEMA_SQL:
            s = stmt
            s = re.sub(r"id\s+INT\s+AUTO_INCREMENT\s+PRIMARY\s+KEY", "id INTEGER PRIMARY KEY AUTOINCREMENT", s, flags=re.IGNORECASE)
            s = re.sub(r"AUTO_INCREMENT\s+PRIMARY\s+KEY", "PRIMARY KEY AUTOINCREMENT", s, flags=re.IGNORECASE)
            s = re.sub(r"INT\s+AUTO_INCREMENT", "INTEGER PRIMARY KEY AUTOINCREMENT", s, flags=re.IGNORECASE)
            s = re.sub(r"ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;", ";", s, flags=re.IGNORECASE)
            raw_conn.execute(s)
        raw_conn.commit()
        raw_conn.close()
    return True
