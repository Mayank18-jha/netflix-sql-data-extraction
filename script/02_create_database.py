"""
Task 2 - Step 2: Create SQLite database and load cleaned data.
Builds database/netflix.db with 3 tables:
    - netflix_titles  (one row per title - the main fact table)
    - netflix_genres  (show_id -> genre, many-to-many junction table)
    - netflix_cast    (show_id -> actor, many-to-many junction table, top 5 billed)

Run from the repo root:
    python scripts/02_create_database.py
"""

import pandas as pd
from pathlib import Path
from db_utils import load_dataframe, list_tables, table_row_count, DB_PATH

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # ensure database/ exists

titles = pd.read_csv(PROCESSED_DIR / "clean_titles.csv")
genres = pd.read_csv(PROCESSED_DIR / "clean_genres.csv")
cast = pd.read_csv(PROCESSED_DIR / "clean_cast.csv")

load_dataframe(titles, "netflix_titles")
load_dataframe(genres, "netflix_genres")
load_dataframe(cast, "netflix_cast")

print(f"Database created: {DB_PATH}")
for t in list_tables():
    print(f"  {t}: {table_row_count(t)} rows")
