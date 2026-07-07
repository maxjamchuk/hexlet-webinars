-- ============================================================================
-- examples.sql
-- Учебные запросы для вебинара по основам SQL.
--
-- Запустить весь файл:
--     sqlite3 superheroes.sqlite ".read examples.sql"
--
-- ...но лучше открыть базу и выполнять запросы ПО ОДНОМУ, чтобы
-- можно было увидеть каждый результат:
--     sqlite3 superheroes.sqlite
--     sqlite> .headers on
--     sqlite> .mode column
--     sqlite> SELECT * FROM heroes LIMIT 5;
--
-- перед тем как работать с этой базой можно на всякий случай создать резервную копию:
--     cp superheroes.sqlite superheroes.sqlite.bak
-- ============================================================================

.headers on
.mode column


-- ############################################################################
-- 1. ПРОСТОЙ SELECT
-- ############################################################################

-- 1.1  Выбрать всех героев (все колонки, все строки).
SELECT * FROM heroes;

-- 1.2  Выбрать только две колонки: псевдоним и настоящее имя.
SELECT alias, real_name FROM heroes;

-- 1.3  Выбрать только активных героев.
SELECT alias, is_active FROM heroes
WHERE is_active = 1;


-- ############################################################################
-- 2. WHERE (фильтрация строк)
-- ############################################################################

-- 2.1  Герои Marvel (publisher_id 1 — это Marvel в наших данных;
--      в разделе JOIN ниже покажем, как фильтровать по названию, а не по id).
SELECT alias, publisher_id FROM heroes
WHERE publisher_id = 1;

-- 2.2  Только антигерои.
SELECT alias, alignment FROM heroes
WHERE alignment = 'antihero';

-- 2.3  Герои с высоким уровнем силы (80 и выше).
SELECT alias, power_level FROM heroes
WHERE power_level >= 80
ORDER BY power_level DESC;

-- 2.4  Герои, чей псевдоним начинается на 'Spider' или 'Bat'.
SELECT alias FROM heroes
WHERE alias LIKE 'Spider%'
   OR alias LIKE 'Bat%';


-- ############################################################################
-- 3. ORDER BY и LIMIT (сортировка и ограничение результата)
-- ############################################################################

-- 3.1  Топ-10 самых сильных героев по уровню силы.
SELECT alias, power_level FROM heroes
WHERE power_level IS NOT NULL
ORDER BY power_level DESC
LIMIT 10;

-- 3.2  10 самых ранних персонажей по году первого появления.
SELECT alias, first_appearance_year FROM heroes
WHERE first_appearance_year IS NOT NULL
ORDER BY first_appearance_year ASC
LIMIT 10;


-- ############################################################################
-- 4. JOIN (объединение таблиц)
-- ############################################################################

-- 4.1  INNER JOIN: каждый герой вместе с названием издателя.
SELECT h.alias, p.name AS publisher
FROM heroes AS h
INNER JOIN publishers AS p ON p.id = h.publisher_id
ORDER BY p.name, h.alias;

-- 4.2  INNER JOIN: каждый герой вместе с названием команды.
--      INNER JOIN скрывает героев без команды (team_id IS NULL).
SELECT h.alias, t.name AS team
FROM heroes AS h
INNER JOIN teams AS t ON t.id = h.team_id
ORDER BY t.name, h.alias;

-- 4.3  LEFT JOIN: все герои, даже те, у кого НЕТ команды.
--      Герои без команды показывают NULL в колонке team.
SELECT h.alias, t.name AS team
FROM heroes AS h
LEFT JOIN teams AS t ON t.id = h.team_id
ORDER BY h.alias;

-- 4.4  LEFT JOIN + WHERE: только герои БЕЗ команды.
SELECT h.alias
FROM heroes AS h
LEFT JOIN teams AS t ON t.id = h.team_id
WHERE t.id IS NULL
ORDER BY h.alias;

-- 4.5  Герои Marvel, отфильтрованные по НАЗВАНИЮ издателя (не по id) через JOIN.
SELECT h.alias, p.name AS publisher
FROM heroes AS h
INNER JOIN publishers AS p ON p.id = h.publisher_id
WHERE p.name = 'Marvel Comics'
ORDER BY h.alias;


-- ############################################################################
-- 5. МНОГИЕ-КО-МНОГИМ (герои <-> способности через hero_powers)
-- ############################################################################

-- 5.1  Все способности одного героя (Spider-Man).
SELECT h.alias, pw.name AS power, pw.category
FROM heroes AS h
INNER JOIN hero_powers AS hp ON hp.hero_id = h.id
INNER JOIN powers      AS pw ON pw.id = hp.power_id
WHERE h.alias = 'Spider-Man'
ORDER BY pw.name;

-- 5.2  Все герои с одной выбранной способностью (Flight).
SELECT pw.name AS power, h.alias
FROM powers AS pw
INNER JOIN hero_powers AS hp ON hp.power_id = pw.id
INNER JOIN heroes      AS h  ON h.id = hp.hero_id
WHERE pw.name = 'Flight'
ORDER BY h.alias;


-- ############################################################################
-- 6. GROUP BY (агрегация) с COUNT и AVG
-- ############################################################################

-- 6.1  Количество героев по издателям.
--      LEFT JOIN оставит издателя в результате, даже если у него нет героев.
SELECT p.name AS publisher, COUNT(h.id) AS hero_count
FROM publishers AS p
LEFT JOIN heroes AS h ON h.publisher_id = p.id
GROUP BY p.id, p.name
ORDER BY hero_count DESC;

-- 6.2  Средний уровень силы по издателям (округлён до 1 знака).
SELECT p.name AS publisher, ROUND(AVG(h.power_level), 1) AS avg_power
FROM heroes AS h
INNER JOIN publishers AS p ON p.id = h.publisher_id
GROUP BY p.name
ORDER BY avg_power DESC;

-- 6.3  Количество героев по командам.
SELECT t.name AS team, COUNT(*) AS hero_count
FROM heroes AS h
INNER JOIN teams AS t ON t.id = h.team_id
GROUP BY t.name
ORDER BY hero_count DESC;

-- 6.4  Самые распространённые способности (сколько героев владеют каждой).
SELECT pw.name AS power, COUNT(*) AS hero_count
FROM powers AS pw
INNER JOIN hero_powers AS hp ON hp.power_id = pw.id
GROUP BY pw.name
ORDER BY hero_count DESC
LIMIT 10;


-- ############################################################################
-- 7. INSERT (добавление строк)
-- ############################################################################

-- 7.0  На случай повторного запуска удаляем старого тестового героя.
DELETE FROM heroes
WHERE alias = 'Test Hero';

-- 7.1  Добавляем нового тестового героя. publisher_id 1 = Marvel в наших данных.
INSERT INTO heroes (alias, real_name, publisher_id, alignment, is_active)
VALUES ('Test Hero', 'Q. A. Tester', 1, 'unknown', 1);

-- 7.2  Проверяем, что герой добавился.
SELECT id, alias, real_name, publisher_id, alignment, is_active
FROM heroes
WHERE alias = 'Test Hero';


-- ############################################################################
-- 8. UPDATE (изменение существующих строк)
-- ############################################################################
-- Всегда используй WHERE в UPDATE, иначе изменишь ВСЕ строки!

-- 8.1  Отправляем тестового героя на пенсию: is_active = 0.
UPDATE heroes
SET is_active = 0
WHERE alias = 'Test Hero';

-- 8.2  Меняем город тестового героя.
UPDATE heroes
SET city = 'Los Angeles'
WHERE alias = 'Test Hero';

-- 8.3  Проверяем изменения.
SELECT alias, city, is_active
FROM heroes
WHERE alias = 'Test Hero';

-- 8.4  ОПАСНО: UPDATE без WHERE изменит ВСЕ строки в таблице.
--      Строка ниже закомментирована специально.
-- UPDATE heroes SET power_level = 100;


-- ############################################################################
-- 9. DELETE (удаление строк)
-- ############################################################################

-- 9.1  Удаляем тестового героя, которого добавили выше.
DELETE FROM heroes
WHERE alias = 'Test Hero';

-- 9.2  Проверяем, что тестовый герой удалён.
SELECT alias
FROM heroes
WHERE alias = 'Test Hero';

-- 9.3  ОПАСНО: DELETE без WHERE удалит ВСЕ строки в таблице.
--      Строка ниже закомментирована специально. Никогда не запускай на реальных данных!
-- DELETE FROM heroes;

-- ############################################################################
-- 10. FOREIGN KEY: пример ошибки
-- ############################################################################

-- Если включён PRAGMA foreign_keys = ON, такой запрос упадёт с ошибкой:
-- FOREIGN KEY constraint failed
--
-- Потому что publisher_id = 999 не существует в таблице publishers.
--
-- INSERT INTO heroes (alias, publisher_id, alignment, is_active)
-- VALUES ('Broken Hero', 999, 'unknown', 1);