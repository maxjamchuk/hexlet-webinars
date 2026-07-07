-- ============================================================================
-- examples.sql
-- Teaching queries for the SQL basics webinar.
--
-- Run the whole file:
--     sqlite3 superheroes.sqlite ".read examples.sql"
--
-- ...but it is much better to open the database and run these ONE AT A TIME so
-- students can see each result:
--     sqlite3 superheroes.sqlite
--     sqlite> .headers on
--     sqlite> .mode column
--     sqlite> SELECT * FROM heroes LIMIT 5;
-- ============================================================================

.headers on
.mode column


-- ############################################################################
-- 1. BASIC SELECT
-- ############################################################################

-- 1.1  Select all heroes (every column, every row).
SELECT * FROM heroes;

-- 1.2  Select only two columns: the alias and the real name.
SELECT alias, real_name FROM heroes;

-- 1.3  Select only heroes that are currently active.
SELECT alias, is_active FROM heroes
WHERE is_active = 1;


-- ############################################################################
-- 2. WHERE (filtering rows)
-- ############################################################################

-- 2.1  Heroes published by Marvel (publisher_id 1 is Marvel in the seed data;
--      the JOIN section below shows how to filter by name instead of id).
SELECT alias, publisher_id FROM heroes
WHERE publisher_id = 1;

-- 2.2  Only antiheroes.
SELECT alias, alignment FROM heroes
WHERE alignment = 'antihero';

-- 2.3  Heroes with a high power level (80 or more).
SELECT alias, power_level FROM heroes
WHERE power_level >= 80
ORDER BY power_level DESC;

-- 2.4  Heroes whose alias starts with 'Spider' or 'Bat'.
SELECT alias FROM heroes
WHERE alias LIKE 'Spider%'
   OR alias LIKE 'Bat%';


-- ############################################################################
-- 3. ORDER BY and LIMIT (sorting and cutting the result)
-- ############################################################################

-- 3.1  Top 10 strongest heroes by power level.
SELECT alias, power_level FROM heroes
WHERE power_level IS NOT NULL
ORDER BY power_level DESC
LIMIT 10;

-- 3.2  The 10 oldest characters by first appearance year.
SELECT alias, first_appearance_year FROM heroes
WHERE first_appearance_year IS NOT NULL
ORDER BY first_appearance_year ASC
LIMIT 10;


-- ############################################################################
-- 4. JOIN (combining tables)
-- ############################################################################

-- 4.1  INNER JOIN: each hero together with its publisher name.
SELECT h.alias, p.name AS publisher
FROM heroes AS h
INNER JOIN publishers AS p ON p.id = h.publisher_id
ORDER BY p.name, h.alias;

-- 4.2  INNER JOIN: each hero together with its team name.
--      INNER JOIN hides heroes that have no team (team_id IS NULL).
SELECT h.alias, t.name AS team
FROM heroes AS h
INNER JOIN teams AS t ON t.id = h.team_id
ORDER BY t.name, h.alias;

-- 4.3  LEFT JOIN: every hero, even the ones WITHOUT a team.
--      Heroes with no team show NULL in the team column.
SELECT h.alias, t.name AS team
FROM heroes AS h
LEFT JOIN teams AS t ON t.id = h.team_id
ORDER BY h.alias;

-- 4.4  LEFT JOIN + WHERE: only the heroes that have NO team.
SELECT h.alias
FROM heroes AS h
LEFT JOIN teams AS t ON t.id = h.team_id
WHERE t.id IS NULL
ORDER BY h.alias;

-- 4.5  Marvel heroes, filtered by publisher NAME (not id) using a JOIN.
SELECT h.alias, p.name AS publisher
FROM heroes AS h
INNER JOIN publishers AS p ON p.id = h.publisher_id
WHERE p.name = 'Marvel Comics'
ORDER BY h.alias;


-- ############################################################################
-- 5. MANY-TO-MANY (heroes <-> powers via hero_powers)
-- ############################################################################

-- 5.1  All powers of one selected hero (Spider-Man).
SELECT h.alias, pw.name AS power, pw.category
FROM heroes AS h
INNER JOIN hero_powers AS hp ON hp.hero_id = h.id
INNER JOIN powers      AS pw ON pw.id = hp.power_id
WHERE h.alias = 'Spider-Man'
ORDER BY pw.name;

-- 5.2  All heroes that have one selected power (Flight).
SELECT pw.name AS power, h.alias
FROM powers AS pw
INNER JOIN hero_powers AS hp ON hp.power_id = pw.id
INNER JOIN heroes      AS h  ON h.id = hp.hero_id
WHERE pw.name = 'Flight'
ORDER BY h.alias;


-- ############################################################################
-- 6. GROUP BY (aggregation) with COUNT and AVG
-- ############################################################################

-- 6.1  Number of heroes per publisher.
SELECT p.name AS publisher, COUNT(*) AS hero_count
FROM heroes AS h
INNER JOIN publishers AS p ON p.id = h.publisher_id
GROUP BY p.name
ORDER BY hero_count DESC;

-- 6.2  Average power level per publisher (rounded to 1 decimal).
SELECT p.name AS publisher, ROUND(AVG(h.power_level), 1) AS avg_power
FROM heroes AS h
INNER JOIN publishers AS p ON p.id = h.publisher_id
GROUP BY p.name
ORDER BY avg_power DESC;

-- 6.3  Number of heroes per team.
SELECT t.name AS team, COUNT(*) AS hero_count
FROM heroes AS h
INNER JOIN teams AS t ON t.id = h.team_id
GROUP BY t.name
ORDER BY hero_count DESC;

-- 6.4  The most common powers (how many heroes have each power).
SELECT pw.name AS power, COUNT(*) AS hero_count
FROM powers AS pw
INNER JOIN hero_powers AS hp ON hp.power_id = pw.id
GROUP BY pw.name
ORDER BY hero_count DESC
LIMIT 10;


-- ############################################################################
-- 7. INSERT (adding rows)
-- ############################################################################

-- 7.1  Add a brand new (test) hero. publisher_id 1 = Marvel in the seed data.
INSERT INTO heroes (alias, real_name, publisher_id, alignment, is_active)
VALUES ('Test Hero', 'Q. A. Tester', 1, 'unknown', 1);


-- ############################################################################
-- 8. UPDATE (changing existing rows)
-- ############################################################################
-- Always UPDATE with a WHERE clause, or you will change EVERY row!

-- 8.1  Retire one hero: set is_active = 0 for the hero with id 1.
UPDATE heroes
SET is_active = 0
WHERE id = 1;

-- 8.2  Update the city of one hero (id 2).
UPDATE heroes
SET city = 'Los Angeles'
WHERE id = 2;


-- ############################################################################
-- 9. DELETE (removing rows)
-- ############################################################################

-- 9.1  Delete the test hero we added above (by alias).
DELETE FROM heroes
WHERE alias = 'Test Hero';

-- 9.2  DANGER: a DELETE without WHERE removes EVERY row in the table.
--      The line below is commented out on purpose. Never run it on real data!
-- DELETE FROM heroes;
