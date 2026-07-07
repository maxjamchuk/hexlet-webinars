-- ============================================================================
-- schema.sql
-- Схема учебной базы данных «superheroes» на SQLite.
--
-- Этот файл создаёт все таблицы и индексы для вебинара по основам SQL.
-- Намеренно простой и подробно прокомментированный, чтобы начинающие могли разобраться.
--
-- Применить вручную:
--     sqlite3 superheroes.sqlite ".read schema.sql"
-- Обычно это делает build_db.py автоматически.
-- ============================================================================

-- Внешние ключи в SQLite по умолчанию выключены, их нужно включать для каждого соединения.
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. publishers (издатели)
--    Компании-издатели комиксов (Marvel, DC, Dark Horse, Image).
-- ----------------------------------------------------------------------------
CREATE TABLE publishers (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    founded_year INTEGER,
    country      TEXT,
    source_url   TEXT
);

-- ----------------------------------------------------------------------------
-- 2. teams (команды)
--    Супергеройские команды (Avengers, X-Men, Justice League, ...).
--    Каждая команда принадлежит ровно одному издателю.
-- ----------------------------------------------------------------------------
CREATE TABLE teams (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    publisher_id INTEGER NOT NULL,
    base_city    TEXT,
    founded_year INTEGER,
    source_url   TEXT,
    FOREIGN KEY (publisher_id) REFERENCES publishers(id),
    UNIQUE (name, publisher_id)
);

-- ----------------------------------------------------------------------------
-- 3. heroes (герои)
--    Главная таблица. Одна строка — один персонаж.
--
--    CHECK-ограничения помогают держать данные чистыми — хороший учебный материал:
--      * alignment должен быть одним из четырёх значений
--      * is_active может быть только 0 или 1 (в SQLite нет настоящего типа boolean)
--      * power_level — NULL или целое число от 1 до 100
-- ----------------------------------------------------------------------------
CREATE TABLE heroes (
    id                    INTEGER PRIMARY KEY,
    alias                 TEXT NOT NULL,
    real_name             TEXT,
    publisher_id          INTEGER NOT NULL,
    team_id               INTEGER,
    alignment             TEXT NOT NULL DEFAULT 'unknown',
    first_appearance_year INTEGER,
    city                  TEXT,
    power_level           INTEGER,
    is_active             INTEGER NOT NULL DEFAULT 1,
    wikidata_qid          TEXT UNIQUE,
    source_url            TEXT,
    FOREIGN KEY (publisher_id) REFERENCES publishers(id),
    FOREIGN KEY (team_id)      REFERENCES teams(id),
    CHECK (alignment IN ('hero', 'antihero', 'villain', 'unknown')),
    CHECK (is_active IN (0, 1)),
    CHECK (power_level IS NULL OR (power_level BETWEEN 1 AND 100))
);

-- ----------------------------------------------------------------------------
-- 4. powers (способности)
--    Каталог способностей. У каждой способности есть категория (physical, mental, ...).
-- ----------------------------------------------------------------------------
CREATE TABLE powers (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL
);

-- ----------------------------------------------------------------------------
-- 5. hero_powers (способности героев)
--    Таблица-связка многие-ко-многим между героями и способностями.
--    У героя может быть много способностей; одна способность может быть у многих героев.
--    ON DELETE CASCADE автоматически удаляет связи, когда удаляется герой или способность.
-- ----------------------------------------------------------------------------
CREATE TABLE hero_powers (
    hero_id  INTEGER NOT NULL,
    power_id INTEGER NOT NULL,
    PRIMARY KEY (hero_id, power_id),
    FOREIGN KEY (hero_id)  REFERENCES heroes(id) ON DELETE CASCADE,
    FOREIGN KEY (power_id) REFERENCES powers(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 6. sources (источники)
--    Происхождение данных: откуда взята каждая строка.
--    entity_type — имя таблицы ('publisher', 'team', 'hero'),
--    entity_id — id записи в этой таблице.
-- ----------------------------------------------------------------------------
CREATE TABLE sources (
    id           INTEGER PRIMARY KEY,
    entity_type  TEXT NOT NULL,
    entity_id    INTEGER NOT NULL,
    source_name  TEXT NOT NULL,
    source_url   TEXT,
    retrieved_at TEXT NOT NULL
);

-- ----------------------------------------------------------------------------
-- Индексы
--    Индексы ускоряют WHERE / JOIN / ORDER BY по этим колонкам.
--    Хорошая тема для обсуждения, когда студенты уже понимают SELECT.
-- ----------------------------------------------------------------------------
CREATE INDEX idx_heroes_alias       ON heroes(alias);
CREATE INDEX idx_heroes_publisher   ON heroes(publisher_id);
CREATE INDEX idx_heroes_team        ON heroes(team_id);
CREATE INDEX idx_heroes_alignment   ON heroes(alignment);
CREATE INDEX idx_heroes_power_level ON heroes(power_level);
CREATE INDEX idx_teams_publisher    ON teams(publisher_id);
CREATE INDEX idx_hero_powers_hero   ON hero_powers(hero_id);
CREATE INDEX idx_hero_powers_power  ON hero_powers(power_id);
