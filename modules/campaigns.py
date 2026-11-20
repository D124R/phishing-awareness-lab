
import sqlite3
from datetime import datetime

DB_NAME = "lab.db"


def init_campaigns():
    """Cria a tabela de campanhas no banco de dados local."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                participant_count INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Rascunho',
                created_at TEXT NOT NULL
            )
        """)


def create_campaign(name, description, participant_count):
    """Cria uma nova campanha educativa."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            INSERT INTO campaigns (
                name,
                description,
                participant_count,
                status,
                created_at
            )
            VALUES (?, ?, ?, 'Rascunho', ?)
        """, (
            name,
            description,
            participant_count,
            datetime.now().strftime("%d/%m/%Y %H:%M")
        ))

        return cursor.lastrowid


def list_campaigns():
    """Retorna todas as campanhas cadastradas."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT *
            FROM campaigns
            ORDER BY id DESC
        """).fetchall()

        return [dict(row) for row in rows]


def approve_campaign(campaign_id):
    """Altera o status de Rascunho para Aprovada."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            UPDATE campaigns
            SET status = 'Aprovada'
            WHERE id = ?
            AND status = 'Rascunho'
        """, (campaign_id,))

        return cursor.rowcount > 0


def complete_campaign(campaign_id):
    """Marca uma campanha aprovada como concluída."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            UPDATE campaigns
            SET status = 'Concluída'
            WHERE id = ?
            AND status = 'Aprovada'
        """, (campaign_id,))

        return cursor.rowcount > 0


# Inicializa a tabela automaticamente
init_campaigns()
