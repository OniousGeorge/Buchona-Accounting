"""SQLite layer for the bank transactions database.

Replaces the notebook's CRUD cells. Fixes the known bug where delete/update
queried a table name ("Transactions") that didn't match the table Create
actually wrote to ("transactions1"), and adds duplicate prevention that
didn't exist before.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "bank_statements.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    statement_id INTEGER PRIMARY KEY,
    account_number TEXT NOT NULL,
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Credit', 'Debit')),
    amount REAL NOT NULL,
    balance REAL NOT NULL,
    UNIQUE(account_number, description, date, amount, balance)
);
"""


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db(reset=False):
    conn = get_connection()
    cur = conn.cursor()
    if reset:
        cur.execute("DROP TABLE IF EXISTS transactions")
        cur.execute("DROP TABLE IF EXISTS transactions1")
    cur.execute(SCHEMA)
    conn.commit()
    conn.close()


def create_transaction(statement):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO transactions
               (account_number, description, date, type, amount, balance)
               VALUES (:Acct_NO, :Description, :Date, :Type, :Amount, :Balance)""",
            statement,
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def list_transactions():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM transactions ORDER BY date")
        return cur.fetchall()
    finally:
        conn.close()


def update_description(statement_id, new_description):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE transactions SET description = ? WHERE statement_id = ?",
            (new_description, statement_id),
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def delete_transaction(statement_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE statement_id = ?", (statement_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def total_by_type():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT type, SUM(amount) FROM transactions GROUP BY type")
        return cur.fetchall()
    finally:
        conn.close()
