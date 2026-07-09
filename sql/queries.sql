/* ============================================================
   TASK 2: SQL for Data Extraction — Netflix Dataset
   Database: netflix.db
   Tables:
     netflix_titles(show_id, type, title, director, country,
                     date_added, release_year, rating,
                     duration_minutes, duration_seasons, description)
     netflix_genres(show_id, genre)
     netflix_cast(show_id, actor)
   ============================================================ */


/* ------------------------------------------------------------
   DAY 7-8: SQL FUNDAMENTALS
   SELECT, WHERE, ORDER BY, LIMIT, GROUP BY, HAVING, JOINs
   ------------------------------------------------------------ */

-- 1. Basic SELECT + WHERE + ORDER BY + LIMIT
-- Top 10 most recent movies added to Netflix
SELECT title, type, date_added, release_year
FROM netflix_titles
WHERE type = 'Movie'
ORDER BY date_added DESC
LIMIT 10;

-- 2. WHERE with multiple conditions
-- TV Shows released after 2018 with a TV-MA rating
SELECT title, release_year, rating
FROM netflix_titles
WHERE type = 'TV Show'
  AND release_year > 2018
  AND rating = 'TV-MA'
ORDER BY release_year DESC;

-- 3. GROUP BY
-- Count of titles by content type
SELECT type, COUNT(*) AS total_titles
FROM netflix_titles
GROUP BY type;

-- 4. GROUP BY + HAVING
-- Countries that have produced more than 200 titles
SELECT country, COUNT(*) AS total_titles
FROM netflix_titles
WHERE country != 'Unknown'
GROUP BY country
HAVING COUNT(*) > 200
ORDER BY total_titles DESC;

-- 5. INNER JOIN
-- Titles with their genres (one row per title-genre pair)
SELECT t.title, t.type, g.genre
FROM netflix_titles t
INNER JOIN netflix_genres g ON t.show_id = g.show_id
LIMIT 20;

-- 6. JOIN + GROUP BY
-- Top 10 genres by number of titles
SELECT g.genre, COUNT(*) AS title_count
FROM netflix_genres g
GROUP BY g.genre
ORDER BY title_count DESC
LIMIT 10;


/* ------------------------------------------------------------
   DAY 9-10: ADVANCED SQL
   Subqueries, CTEs (WITH clause), window functions, VIEWS
   ------------------------------------------------------------ */

-- 7. Subquery in WHERE
-- Titles from countries that have produced more than 200 titles
SELECT title, country
FROM netflix_titles
WHERE country IN (
    SELECT country
    FROM netflix_titles
    WHERE country != 'Unknown'
    GROUP BY country
    HAVING COUNT(*) > 200
);

-- 8. Correlated subquery
-- Directors whose titles are all rated 'TV-MA' (directors with only mature content)
SELECT DISTINCT t1.director
FROM netflix_titles t1
WHERE t1.director != 'Unknown'
  AND NOT EXISTS (
      SELECT 1 FROM netflix_titles t2
      WHERE t2.director = t1.director
        AND t2.rating != 'TV-MA'
  );

-- 9. CTE (WITH clause)
-- Yearly content additions, then filter to years with 200+ additions
WITH yearly_additions AS (
    SELECT strftime('%Y', date_added) AS year_added, COUNT(*) AS additions
    FROM netflix_titles
    WHERE date_added IS NOT NULL
    GROUP BY year_added
)
SELECT year_added, additions
FROM yearly_additions
WHERE additions >= 200
ORDER BY year_added;

-- 10. CTE with JOIN
-- Top director per genre (by title count), using a CTE to pre-aggregate
WITH director_genre_counts AS (
    SELECT t.director, g.genre, COUNT(*) AS cnt
    FROM netflix_titles t
    JOIN netflix_genres g ON t.show_id = g.show_id
    WHERE t.director != 'Unknown'
    GROUP BY t.director, g.genre
)
SELECT genre, director, cnt
FROM director_genre_counts
WHERE cnt >= 5
ORDER BY genre, cnt DESC;

-- 11. Window function: ROW_NUMBER()
-- Rank each title within its release year by duration (longest movie per year)
SELECT title, release_year, duration_minutes,
       ROW_NUMBER() OVER (PARTITION BY release_year ORDER BY duration_minutes DESC) AS rank_in_year
FROM netflix_titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL;

-- 12. Window function: RANK() and LAG()
-- Year-over-year change in number of titles added
WITH yearly AS (
    SELECT strftime('%Y', date_added) AS year_added, COUNT(*) AS additions
    FROM netflix_titles
    WHERE date_added IS NOT NULL
    GROUP BY year_added
)
SELECT year_added,
       additions,
       LAG(additions) OVER (ORDER BY year_added) AS prev_year_additions,
       additions - LAG(additions) OVER (ORDER BY year_added) AS yoy_change
FROM yearly
ORDER BY year_added;

-- 13. Window function: RANK() for top actor appearances
SELECT actor, appearances, RANK() OVER (ORDER BY appearances DESC) AS actor_rank
FROM (
    SELECT actor, COUNT(*) AS appearances
    FROM netflix_cast
    GROUP BY actor
) actor_counts
LIMIT 15;

-- 14. VIEW: reusable view for movie-only records with clean duration
CREATE VIEW IF NOT EXISTS v_movies AS
SELECT show_id, title, director, country, release_year,
       rating, duration_minutes, date_added
FROM netflix_titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL;

-- Example usage of the view
SELECT * FROM v_movies ORDER BY duration_minutes DESC LIMIT 10;

-- 15. VIEW: reusable view for genre-level summary stats
CREATE VIEW IF NOT EXISTS v_genre_summary AS
SELECT g.genre,
       COUNT(*) AS title_count,
       SUM(CASE WHEN t.type = 'Movie' THEN 1 ELSE 0 END) AS movie_count,
       SUM(CASE WHEN t.type = 'TV Show' THEN 1 ELSE 0 END) AS tv_show_count
FROM netflix_genres g
JOIN netflix_titles t ON g.show_id = t.show_id
GROUP BY g.genre;

-- Example usage of the view
SELECT * FROM v_genre_summary ORDER BY title_count DESC LIMIT 10;
