-- ============================================================================
-- schema.sql
-- Database schema for the "superheroes" educational SQLite database.
--
-- This file creates every table and index used in the SQL basics webinar.
-- It is intentionally simple and heavily commented so beginners can read it.
--
-- You can apply it by hand with:
--     sqlite3 superheroes.sqlite ".read schema.sql"
-- but normally build_db.py runs it for you.
-- ============================================================================

-- Foreign keys are OFF by default in SQLite and must be enabled per connection.
PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- 1. publishers
--    The comic book companies (Marvel, DC, Dark Horse, Image).
-- ----------------------------------------------------------------------------
CREATE TABLE publishers (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE,
    founded_year INTEGER,
    country      TEXT,
    source_url   TEXT
);

-- ----------------------------------------------------------------------------
-- 2. teams
--    Super teams (Avengers, X-Men, Justice League, ...).
--    Each team belongs to exactly one publisher.
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
-- 3. heroes
--    The main table. One row per character.
--
--    CHECK constraints keep the data clean and are great teaching material:
--      * alignment must be one of four known values
--      * is_active must be 0 or 1 (SQLite has no real boolean type)
--      * power_level must be NULL or an integer from 1 to 100
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
-- 4. powers
--    A catalog of abilities. Each power has a category (physical, mental, ...).
-- ----------------------------------------------------------------------------
CREATE TABLE powers (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL
);

-- ----------------------------------------------------------------------------
-- 5. hero_powers
--    Many-to-many link table between heroes and powers.
--    A hero can have many powers; a power can belong to many heroes.
--    ON DELETE CASCADE cleans up links automatically when a hero or power
--    is removed.
-- ----------------------------------------------------------------------------
CREATE TABLE hero_powers (
    hero_id  INTEGER NOT NULL,
    power_id INTEGER NOT NULL,
    PRIMARY KEY (hero_id, power_id),
    FOREIGN KEY (hero_id)  REFERENCES heroes(id) ON DELETE CASCADE,
    FOREIGN KEY (power_id) REFERENCES powers(id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 6. sources
--    Provenance / metadata: where each row of data came from.
--    entity_type is the table name ('publisher', 'team', 'hero'),
--    entity_id is the id inside that table.
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
-- Indexes
--    Indexes make WHERE / JOIN / ORDER BY on these columns faster.
--    They are a good talking point once students understand SELECT.
-- ----------------------------------------------------------------------------
CREATE INDEX idx_heroes_alias       ON heroes(alias);
CREATE INDEX idx_heroes_publisher   ON heroes(publisher_id);
CREATE INDEX idx_heroes_team        ON heroes(team_id);
CREATE INDEX idx_heroes_alignment   ON heroes(alignment);
CREATE INDEX idx_heroes_power_level ON heroes(power_level);
CREATE INDEX idx_teams_publisher    ON teams(publisher_id);
CREATE INDEX idx_hero_powers_hero   ON hero_powers(hero_id);
CREATE INDEX idx_hero_powers_power  ON hero_powers(power_id);
