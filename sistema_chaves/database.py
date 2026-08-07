import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "database.db"


def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def inicializar_banco():
    """Cria estruturas adicionadas pela aplicação sem apagar dados existentes."""
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS administradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prontuario TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()
