"""Módulo de banco de dados do agente."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "agent.db"


def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão SQLite para o banco do agente."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database() -> None:
    """Inicializa o banco de dados do agente, criando tabelas básicas."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_state (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT
            )
            """
        )
        conn.commit()
