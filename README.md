# Netflix SQL Data Extraction — Task 2

**Internship:** Apexplanet Data Analytics Internship
**Timeline:** 7 Days
**Dataset:** Netflix Movies & TV Shows (`data/raw/netflix_movies.csv`, 8,807 titles)

## Objective
Master SQL queries for data extraction and analysis — from fundamentals
(SELECT, WHERE, JOINs, GROUP BY) through advanced techniques (CTEs, window
functions, views) — and integrate SQL with Python for automated, repeatable
analysis.

## Project Structure

```
netflix-sql-data-extraction/
├── data/
│   ├── raw/                       # original dataset
│   └── processed/                 # cleaned + normalized CSVs
├── database/
│   └── netflix.db                 # generated SQLite database
├── scripts/
│   ├── 01_data_cleaning.py
│   ├── 02_create_database.py
│   └── db_utils.py                # reusable database utility module
├── sql/
│   └── queries.sql                # fundamentals + advanced SQL
├── notebooks/
│   └── sql_python_integration.ipynb
├── reports/
│   └── figure/                    # EDA Charts
└── README.md
```

## Database Schema

```
netflix_titles (show_id PK, type, title, director, country, date_added,
                release_year, rating, duration_minutes, duration_seasons, description)
netflix_genres (show_id FK -> netflix_titles, genre)
netflix_cast   (show_id FK -> netflix_titles, actor)
```
Genres and cast were normalized into separate junction tables (rather than
kept as comma-separated strings) so that JOINs, GROUP BY, and HAVING could be
practiced realistically.

## How to Run

```bash
git clone <repo-url>
cd netflix-sql-data-extraction
pip install -r requirements.txt

# 1. Clean the raw data
python scripts/01_data_cleaning.py

# 2. Build the SQLite database
python scripts/02_create_database.py

# 3. (Optional) create the reusable views from the SQL file
python -c "import sys; sys.path.insert(0, 'scripts'); from db_utils import execute_script; execute_script('sql/queries.sql')"

# 4. Open the analysis notebook
jupyter notebook notebooks/sql_python_integration.ipynb
```

## Business Questions Answered (in the notebook)
1. Top 5 genres by number of titles
2. Monthly trend of content added to Netflix
3. Top 10 countries by content produced
4. Movie vs TV Show split by release year (last 10 years)
5. Top 10 most-featured actors
6. Content rating distribution
7. Average movie duration trend over time
8. Directors with the largest, most consistent catalogs (5+ titles)
9. Year-over-year growth rate in content additions (window functions)
10. Genre skew — Movie-heavy vs TV-heavy genres (via `v_genre_summary` view)

## Key Findings
- International Movies, Dramas, and Comedies dominate the catalog.
- Content additions to Netflix accelerated sharply from 2017–2020.
- The US, India, and UK are the top three content-producing countries.
- Average movie runtime has trended slightly shorter in recent release years.
- A small group of prolific directors (5+ titles each) account for a
  disproportionate share of total content — useful for partnership analysis.


