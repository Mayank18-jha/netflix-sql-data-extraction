"""
Task 2 - Step 1: Data Cleaning
Cleans the raw Netflix dataset and prepares it for SQLite import.
Also splits multi-valued columns (cast, listed_in) into long/normalized
form so they can be loaded into separate junction tables later
(needed for realistic JOIN / GROUP BY / HAVING practice).

Run from the repo root:
    python scripts/01_data_cleaning.py
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path

# Paths are relative to the repo root (script lives in scripts/, data in data/)
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "netflix_movies.csv"
OUT_DIR = BASE_DIR / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(RAW_PATH)

# ---- 1. Basic cleaning ----
df["director"] = df["director"].fillna("Unknown")
df["cast"] = df["cast"].fillna("Unknown")
df["country"] = df["country"].fillna("Unknown")
df["rating"] = df["rating"].fillna("Not Rated")

# date_added -> proper datetime, drop rows where it's unparseable but keep title
df["date_added"] = df["date_added"].str.strip()
df["date_added_clean"] = pd.to_datetime(df["date_added"], errors="coerce")

# ---- 2. Split duration into numeric fields ----
# Movies: "90 min" -> minutes
# TV Shows: "3 Seasons" / "1 Season" -> seasons
def parse_duration(row):
    dur = row["duration"]
    if pd.isna(dur):
        return np.nan, np.nan
    dur = str(dur)
    if "min" in dur:
        m = re.search(r"(\d+)", dur)
        return (int(m.group(1)) if m else np.nan), np.nan
    elif "Season" in dur:
        m = re.search(r"(\d+)", dur)
        return np.nan, (int(m.group(1)) if m else np.nan)
    return np.nan, np.nan

df[["duration_minutes", "duration_seasons"]] = df.apply(
    lambda r: pd.Series(parse_duration(r)), axis=1
)

# ---- 3. Main cleaned table (one row per title) ----
main_cols = [
    "show_id", "type", "title", "director", "country",
    "date_added_clean", "release_year", "rating",
    "duration_minutes", "duration_seasons", "description"
]
titles_clean = df[main_cols].rename(columns={"date_added_clean": "date_added"})
titles_clean.to_csv(OUT_DIR / "clean_titles.csv", index=False)

# ---- 4. Genre junction table (listed_in can have multiple comma-separated genres) ----
genre_rows = []
for _, row in df[["show_id", "listed_in"]].dropna().iterrows():
    for genre in row["listed_in"].split(","):
        genre_rows.append({"show_id": row["show_id"], "genre": genre.strip()})
genres_long = pd.DataFrame(genre_rows)
genres_long.to_csv(OUT_DIR / "clean_genres.csv", index=False)

# ---- 5. Cast junction table (top billed actors only, first 5 per title, to keep it manageable) ----
cast_rows = []
for _, row in df[["show_id", "cast"]].dropna().iterrows():
    if row["cast"] == "Unknown":
        continue
    actors = [a.strip() for a in row["cast"].split(",")][:5]
    for actor in actors:
        cast_rows.append({"show_id": row["show_id"], "actor": actor})
cast_long = pd.DataFrame(cast_rows)
cast_long.to_csv(OUT_DIR / "clean_cast.csv", index=False)

print("Cleaned files written to data/processed/:")
print(f"  clean_titles.csv -> {titles_clean.shape}")
print(f"  clean_genres.csv -> {genres_long.shape}")
print(f"  clean_cast.csv   -> {cast_long.shape}")
