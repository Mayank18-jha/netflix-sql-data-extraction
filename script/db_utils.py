"""
db_utils.py
-----------
Reusable SQLite database utility module for the Netflix Data Extraction task.

Provides a small, reusable set of helper functions so any script or notebook
can connect to, load data into, and query the netflix.db SQLite database
without repeating boilerplate. Import this module wherever DB access is needed:

    from db_utils import get_connection, run_query, load_dataframe, execute_script

Author: Mayank | Apexplanet Internship - Task 2
"""

import sqlite3
import pandas as pd
from pathlib import Path
from contextlib import contextmanager

# database/ lives one level up from scripts/, at the repo root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "netflix.db"


@contextmanager
def get_connection(db_path: str = None):
    """
    Context-managed SQLite connection.
    Usage:
        with get_connection() as conn:
            df = pd.read_sql("SELECT * FROM netflix_titles LIMIT 5", conn)
    """
    conn = sqlite3.connect(db_path or DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def run_query(query: str, params: tuple = (), db_path: str = None) -> pd.DataFrame:
    """
    Run a SELECT query and return results as a pandas DataFrame.
    """
    with get_connection(db_path) as conn:
        return pd.read_sql_query(query, conn, params=params)


def execute_statement(statement: str, params: tuple = (), db_path: str = None) -> None:
    """
    Execute a single non-SELECT statement (INSERT/UPDATE/DELETE/CREATE/DROP).
    """
    with get_connection(db_path) as conn:
        conn.execute(statement, params)
        conn.commit()


def execute_script(sql_script_path: str, db_path: str = None) -> None:
    """
    Execute a full .sql file containing one or more statements
    (e.g. sql/queries.sql). Useful for creating views or running a batch
    of setup statements at once.
    """
    with get_connection(db_path) as conn:
        with open(sql_script_path, "r") as f:
            conn.executescript(f.read())
        conn.commit()


def load_dataframe(df: pd.DataFrame, table_name: str, if_exists: str = "replace",
                    db_path: str = None) -> None:
    """
    Load a pandas DataFrame into a SQLite table.
    if_exists: 'replace' | 'append' | 'fail'
    """
    with get_connection(db_path) as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)


def list_tables(db_path: str = None) -> list:
    """
    Return a list of all table names currently in the database.
    """
    result = run_query(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",
        db_path=db_path
    )
    return result["name"].tolist()


def table_row_count(table_name: str, db_path: str = None) -> int:
    """
    Return the number of rows in a given table.
    """
    result = run_query(f"SELECT COUNT(*) AS cnt FROM {table_name};", db_path=db_path)
    return int(result.loc[0, "cnt"])


if __name__ == "__main__":
    # Quick smoke test when run directly: python scripts/db_utils.py
    print("Tables in database:", list_tables())
    for t in list_tables():
        print(f"  {t}: {table_row_count(t)} rows")
