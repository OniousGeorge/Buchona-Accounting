"""SQLite layer for the bank transactions database.

Replaces the notebook's CRUD cells. Fixes the known bug where delete/update
queried a table name ("Transactions") that didn't match the table Create
actually wrote to ("transactions1"), and adds duplicate prevention that
didn't exist before.
"""
import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "bank_statements.db"

DEBIT_SCHEMA = """
CREATE TABLE IF NOT EXISTS debit_transactions (
    debit_statement_id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    balance REAL NOT NULL,
    occurrence INTEGER NOT NULL,
    UNIQUE(description, date, amount, balance, occurrence)
    );
    
"""

CREDIT_SCHEMA="""CREATE TABLE IF NOT EXISTS credit_transactions (
    credit_statement_id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    occurrence INTEGER NOT NULL,
    UNIQUE(description, date, amount, occurrence)
);

"""


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db(reset=False):
    DATA_DIR.mkdir(exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()
    if reset:
        cur.execute("DROP TABLE IF EXISTS debit_transactions")
        cur.execute("DROP TABLE IF EXISTS credit_transactions")
    cur.execute(DEBIT_SCHEMA)
    cur.execute(CREDIT_SCHEMA)

    conn.commit()
    conn.close()


def create_debit_transaction(statement):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO debit_transactions
               (description, date, amount, balance, occurrence)
               VALUES ( :Description, :Date, :Amount, :Balance, :Occurrence)""",
            statement,
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            return None
        raise
    finally:
        conn.close()

def create_credit_transaction(statement):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO credit_transactions
               (description, date, amount, category, occurrence)
               VALUES ( :Description, :Date, :Amount, :Category, :Occurrence)""",
            statement,
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            return None
        raise
    finally:
        conn.close()

def list_debit_transactions():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM debit_transactions ORDER BY date")
        return cur.fetchall()
    finally:
        conn.close()

def list_credit_transactions():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM credit_transactions ORDER BY date")
        return cur.fetchall()
    finally:
        conn.close()

def update_debit_description(statement_id, new_description):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE debit_transactions SET description = ? WHERE debit_statement_id = ?",
            (new_description, statement_id),
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def update_credit_description(statement_id, new_description):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE credit_transactions SET description = ? WHERE credit_statement_id = ?",
            (new_description, statement_id),
        )
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def delete_debit_transaction(statement_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM debit_transactions WHERE debit_statement_id = ?", (statement_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def delete_credit_transaction(statement_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM credit_transactions WHERE credit_statement_id = ?", (statement_id,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

def list_all():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""SELECT 'debit' AS account, description, date, amount FROM debit_transactions
                    UNION ALL SELECT 'credit', description, date, amount FROM credit_transactions ORDER BY date""")
        return cur.fetchall()
    finally:
        conn.close()

if __name__ == "__main__":
    trans=list_credit_transactions()
    for i, s in enumerate(trans, 1):
        print(f"{i}. {s}")