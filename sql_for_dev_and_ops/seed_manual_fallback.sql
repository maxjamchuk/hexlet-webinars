-- ============================================================================
-- seed_manual_fallback.sql
-- Offline fallback data for the superheroes database.
--
-- build_db.py runs this ONLY when it cannot fetch live data from the internet.
-- It contains commonly-known factual information about well-known characters
-- (names, publisher, team, first appearance year, city). It deliberately
-- contains NO copied descriptions, biographies, or plot summaries.
--
-- Fields that are unknown are stored as NULL.
-- The power_level column is an ARTIFICIAL teaching value (1-100), not canon.
-- The is_active column is a SIMPLIFIED teaching flag, not a canonical status.
-- wikidata_qid is left NULL here because these rows were entered by hand and
-- their QIDs were not individually verified.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- --------------------------------------------------------------------------
-- Publishers
-- --------------------------------------------------------------------------
INSERT INTO publishers (id, name, founded_year, country, source_url) VALUES
    (1, 'Marvel Comics',     1939, 'United States', 'https://www.wikidata.org/wiki/Q173496'),
    (2, 'DC Comics',         1934, 'United States', 'https://www.wikidata.org/wiki/Q2924461'),
    (3, 'Dark Horse Comics', 1986, 'United States', 'https://www.wikidata.org/wiki/Q373933'),
    (4, 'Image Comics',      1992, 'United States', 'https://www.wikidata.org/wiki/Q913301');

-- --------------------------------------------------------------------------
-- Teams
-- --------------------------------------------------------------------------
INSERT INTO teams (id, name, publisher_id, base_city, founded_year, source_url) VALUES
    (1, 'Avengers',                1, 'New York City', 1963, NULL),
    (2, 'X-Men',                   1, 'Salem Center',  1963, NULL),
    (3, 'Fantastic Four',          1, 'New York City', 1961, NULL),
    (4, 'Guardians of the Galaxy', 1, NULL,            1969, NULL),
    (5, 'Justice League',          2, NULL,            1960, NULL),
    (6, 'Teen Titans',             2, NULL,            1964, NULL),
    (7, 'Suicide Squad',           2, NULL,            1959, NULL),
    (8, 'B.P.R.D.',                3, 'Fairfield',     NULL, NULL);

-- --------------------------------------------------------------------------
-- Powers catalog
-- --------------------------------------------------------------------------
INSERT INTO powers (id, name, category) VALUES
    (1,  'Superhuman Strength',  'physical'),
    (2,  'Superhuman Durability','physical'),
    (3,  'Superhuman Agility',   'physical'),
    (4,  'Enhanced Senses',      'physical'),
    (5,  'Flight',               'movement'),
    (6,  'Super Speed',          'movement'),
    (7,  'Wall-Crawling',        'movement'),
    (8,  'Teleportation',        'movement'),
    (9,  'Telepathy',            'mental'),
    (10, 'Telekinesis',          'mental'),
    (11, 'Mind Control',         'mental'),
    (12, 'Genius Intelligence',  'mental'),
    (13, 'Magic',                'mystical'),
    (14, 'Immortality',          'mystical'),
    (15, 'Energy Manipulation',  'mystical'),
    (16, 'Weather Control',      'mystical'),
    (17, 'Powered Armor',        'technology'),
    (18, 'Advanced Technology',  'technology'),
    (19, 'Utility Gadgets',      'equipment'),
    (20, 'Bow and Arrows',       'equipment'),
    (21, 'Shield',               'equipment'),
    (22, 'Hammer',               'equipment'),
    (23, 'Trident',              'equipment'),
    (24, 'Martial Arts',         'skill'),
    (25, 'Master Tactician',     'skill'),
    (26, 'Marksmanship',         'skill'),
    (27, 'Stealth',              'skill'),
    (28, 'Swordsmanship',        'skill'),
    (29, 'Healing Factor',       'biological'),
    (30, 'Shapeshifting',        'biological'),
    (31, 'Claws',                'biological'),
    (32, 'Toxin Immunity',       'biological'),
    (33, 'Cosmic Power',         'cosmic'),
    (34, 'Energy Projection',    'cosmic'),
    (35, 'Force Field',          'cosmic'),
    (36, 'Unknown',              'unknown');

-- --------------------------------------------------------------------------
-- Heroes
-- columns: id, alias, real_name, publisher_id, team_id, alignment,
--          first_appearance_year, city, power_level, is_active,
--          wikidata_qid, source_url
-- --------------------------------------------------------------------------
INSERT INTO heroes
    (id, alias, real_name, publisher_id, team_id, alignment, first_appearance_year, city, power_level, is_active, wikidata_qid, source_url)
VALUES
    -- Marvel Comics
    (1,  'Spider-Man',       'Peter Parker',     1, NULL, 'hero',     1962, 'New York City', 80, 1, NULL, NULL),
    (2,  'Iron Man',         'Tony Stark',       1, 1,    'hero',     1963, 'New York City', 82, 1, NULL, NULL),
    (3,  'Captain America',  'Steve Rogers',     1, 1,    'hero',     1941, 'New York City', 75, 1, NULL, NULL),
    (4,  'Thor',             'Thor Odinson',     1, 1,    'hero',     1962, 'Asgard',        95, 1, NULL, NULL),
    (5,  'Hulk',             'Bruce Banner',     1, 1,    'hero',     1962, NULL,            95, 1, NULL, NULL),
    (6,  'Black Widow',      'Natasha Romanoff', 1, 1,    'hero',     1964, NULL,            55, 1, NULL, NULL),
    (7,  'Hawkeye',          'Clint Barton',     1, 1,    'hero',     1964, NULL,            52, 1, NULL, NULL),
    (8,  'Wolverine',        'Logan',            1, 2,    'antihero', 1974, NULL,            82, 1, NULL, NULL),
    (9,  'Cyclops',          'Scott Summers',    1, 2,    'hero',     1963, NULL,            72, 1, NULL, NULL),
    (10, 'Storm',            'Ororo Munroe',     1, 2,    'hero',     1975, NULL,            80, 1, NULL, NULL),
    (11, 'Jean Grey',        'Jean Grey',        1, 2,    'hero',     1963, NULL,            88, 1, NULL, NULL),
    (12, 'Professor X',      'Charles Xavier',   1, 2,    'hero',     1963, 'Salem Center',  82, 1, NULL, NULL),
    (13, 'Magneto',          'Max Eisenhardt',   1, NULL, 'villain',  1963, NULL,            85, 1, NULL, NULL),
    (14, 'Deadpool',         'Wade Wilson',      1, NULL, 'antihero', 1991, 'New York City', 78, 1, NULL, NULL),
    (15, 'Doctor Strange',   'Stephen Strange',  1, NULL, 'hero',     1963, 'New York City', 88, 1, NULL, NULL),
    (16, 'Black Panther',    'T''Challa',        1, 1,    'hero',     1966, NULL,            78, 1, NULL, NULL),
    (17, 'Captain Marvel',   'Carol Danvers',    1, 1,    'hero',     1968, NULL,            90, 1, NULL, NULL),
    (18, 'Scarlet Witch',    'Wanda Maximoff',   1, 1,    'antihero', 1964, NULL,            88, 1, NULL, NULL),
    (19, 'Vision',           NULL,               1, 1,    'hero',     1968, NULL,            82, 1, NULL, NULL),
    (20, 'Mister Fantastic', 'Reed Richards',    1, 3,    'hero',     1961, 'New York City', 78, 1, NULL, NULL),
    (21, 'Invisible Woman',  'Susan Storm',      1, 3,    'hero',     1961, 'New York City', 80, 1, NULL, NULL),
    (22, 'Human Torch',      'Johnny Storm',     1, 3,    'hero',     1961, 'New York City', 78, 1, NULL, NULL),
    (23, 'Thing',            'Ben Grimm',        1, 3,    'hero',     1961, 'New York City', 82, 1, NULL, NULL),
    (24, 'Star-Lord',        'Peter Quill',      1, 4,    'hero',     1976, NULL,            60, 1, NULL, NULL),
    (25, 'Gamora',           NULL,               1, 4,    'antihero', 1975, NULL,            70, 1, NULL, NULL),
    (26, 'Groot',            NULL,               1, 4,    'hero',     1960, NULL,            70, 1, NULL, NULL),
    (27, 'Rocket Raccoon',   NULL,               1, 4,    'hero',     1976, NULL,            55, 1, NULL, NULL),
    (28, 'Venom',            'Eddie Brock',      1, NULL, 'antihero', 1988, 'New York City', 80, 1, NULL, NULL),
    (29, 'Green Goblin',     'Norman Osborn',    1, NULL, 'villain',  1964, 'New York City', 72, 1, NULL, NULL),
    (30, 'Thanos',           NULL,               1, NULL, 'villain',  1973, NULL,            96, 1, NULL, NULL),
    (31, 'Silver Surfer',    'Norrin Radd',      1, NULL, 'hero',     1966, NULL,            92, 1, NULL, NULL),
    (32, 'Daredevil',        'Matt Murdock',     1, NULL, 'hero',     1964, 'New York City', 62, 1, NULL, NULL),

    -- DC Comics
    (33, 'Superman',          'Clark Kent',    2, 5,    'hero',     1938, 'Metropolis',   98, 1, NULL, NULL),
    (34, 'Batman',            'Bruce Wayne',   2, 5,    'hero',     1939, 'Gotham City',  70, 1, NULL, NULL),
    (35, 'Wonder Woman',      'Diana Prince',  2, 5,    'hero',     1941, 'Themyscira',   90, 1, NULL, NULL),
    (36, 'The Flash',         'Barry Allen',   2, 5,    'hero',     1956, 'Central City', 88, 1, NULL, NULL),
    (37, 'Green Lantern',     'Hal Jordan',    2, 5,    'hero',     1959, 'Coast City',   85, 1, NULL, NULL),
    (38, 'Aquaman',           'Arthur Curry',  2, 5,    'hero',     1941, 'Atlantis',     80, 1, NULL, NULL),
    (39, 'Cyborg',            'Victor Stone',  2, 5,    'hero',     1980, NULL,           75, 1, NULL, NULL),
    (40, 'Green Arrow',       'Oliver Queen',  2, NULL, 'hero',     1941, 'Star City',    55, 1, NULL, NULL),
    (41, 'Shazam',            'Billy Batson',  2, NULL, 'hero',     1940, NULL,           88, 1, NULL, NULL),
    (42, 'Nightwing',         'Dick Grayson',  2, 6,    'hero',     1940, 'Bludhaven',    65, 1, NULL, NULL),
    (43, 'Batgirl',           'Barbara Gordon',2, NULL, 'hero',     1967, 'Gotham City',  55, 1, NULL, NULL),
    (44, 'Supergirl',         'Kara Zor-El',   2, NULL, 'hero',     1959, 'Metropolis',   92, 1, NULL, NULL),
    (45, 'Harley Quinn',      'Harleen Quinzel',2, 7,   'antihero', 1992, 'Gotham City',  45, 1, NULL, NULL),
    (46, 'Joker',             NULL,            2, NULL, 'villain',  1940, 'Gotham City',  40, 1, NULL, NULL),
    (47, 'Lex Luthor',        'Lex Luthor',    2, NULL, 'villain',  1940, 'Metropolis',   60, 1, NULL, NULL),
    (48, 'Catwoman',          'Selina Kyle',   2, NULL, 'antihero', 1940, 'Gotham City',  45, 1, NULL, NULL),
    (49, 'Deathstroke',       'Slade Wilson',  2, NULL, 'villain',  1980, NULL,           78, 1, NULL, NULL),
    (50, 'Raven',             'Rachel Roth',   2, 6,    'hero',     1980, NULL,           85, 1, NULL, NULL),
    (51, 'Starfire',          'Koriand''r',    2, 6,    'hero',     1980, NULL,           80, 1, NULL, NULL),
    (52, 'Zatanna',           'Zatanna Zatara',2, NULL, 'hero',     1964, NULL,           82, 1, NULL, NULL),
    (53, 'Martian Manhunter', 'J''onn J''onzz',2, 5,    'hero',     1955, NULL,           90, 1, NULL, NULL),

    -- Dark Horse Comics
    (54, 'Hellboy',    'Anung un Rama',    3, 8,    'antihero', 1993, NULL, 78, 1, NULL, NULL),
    (55, 'Abe Sapien', 'Abraham Sapien',   3, 8,    'hero',     1994, NULL, 65, 1, NULL, NULL),
    (56, 'The Mask',   'Stanley Ipkiss',   3, NULL, 'antihero', 1987, NULL, 70, 1, NULL, NULL),
    (57, 'Concrete',   'Ronald Lithgow',   3, NULL, 'hero',     1986, NULL, 60, 0, NULL, NULL),
    (58, 'Barb Wire',  'Barbara Kopetski', 3, NULL, 'antihero', 1994, NULL, 40, 0, NULL, NULL),

    -- Image Comics
    (59, 'Spawn',         'Al Simmons',       4, NULL, 'antihero', 1992, 'New York City', 88, 1, NULL, NULL),
    (60, 'Invincible',    'Mark Grayson',     4, NULL, 'hero',     2003, NULL,            90, 1, NULL, NULL),
    (61, 'Savage Dragon', NULL,               4, NULL, 'hero',     1992, 'Chicago',       78, 1, NULL, NULL),
    (62, 'Witchblade',    'Sara Pezzini',     4, NULL, 'hero',     1995, 'New York City', 72, 1, NULL, NULL),
    (63, 'Shadowhawk',    'Paul Johnstone',   4, NULL, 'antihero', 1992, NULL,            55, 0, NULL, NULL),
    (64, 'The Maxx',      NULL,               4, NULL, 'hero',     1993, NULL,            65, 0, NULL, NULL);

-- --------------------------------------------------------------------------
-- Hero powers (many-to-many links)
-- --------------------------------------------------------------------------
INSERT INTO hero_powers (hero_id, power_id) VALUES
    -- Marvel
    (1, 7), (1, 1), (1, 3), (1, 4),
    (2, 17), (2, 5), (2, 34), (2, 12),
    (3, 1), (3, 3), (3, 21), (3, 25),
    (4, 1), (4, 5), (4, 22), (4, 16),
    (5, 1), (5, 2), (5, 29),
    (6, 24), (6, 26), (6, 27),
    (7, 20), (7, 26),
    (8, 31), (8, 29), (8, 4),
    (9, 34),
    (10, 16), (10, 5),
    (11, 9), (11, 10),
    (12, 9), (12, 11), (12, 12),
    (13, 15), (13, 5), (13, 35),
    (14, 29), (14, 24), (14, 28),
    (15, 13), (15, 8), (15, 14),
    (16, 1), (16, 3), (16, 24), (16, 4),
    (17, 5), (17, 1), (17, 34), (17, 33),
    (18, 13), (18, 10),
    (19, 5), (19, 30), (19, 34), (19, 12),
    (20, 30), (20, 12),
    (21, 35),
    (22, 5), (22, 34),
    (23, 1), (23, 2),
    (24, 26), (24, 5),
    (25, 24), (25, 28), (25, 1),
    (26, 1), (26, 30), (26, 2),
    (27, 26), (27, 12), (27, 18),
    (28, 1), (28, 7), (28, 30),
    (29, 5), (29, 1), (29, 12), (29, 18),
    (30, 1), (30, 2), (30, 33), (30, 15),
    (31, 5), (31, 33), (31, 34),
    (32, 4), (32, 24), (32, 3),
    -- DC
    (33, 1), (33, 5), (33, 34), (33, 2),
    (34, 24), (34, 25), (34, 19), (34, 12),
    (35, 1), (35, 5), (35, 28), (35, 24),
    (36, 6),
    (37, 15), (37, 5), (37, 35),
    (38, 1), (38, 23), (38, 11),
    (39, 18), (39, 34), (39, 12),
    (40, 20), (40, 26), (40, 24),
    (41, 1), (41, 5), (41, 6), (41, 13),
    (42, 24), (42, 3), (42, 25),
    (43, 24), (43, 12), (43, 19),
    (44, 1), (44, 5), (44, 34), (44, 2),
    (45, 24), (45, 3), (45, 32),
    (46, 25), (46, 32),
    (47, 12), (47, 18), (47, 17),
    (48, 24), (48, 3), (48, 27),
    (49, 1), (49, 24), (49, 28), (49, 29),
    (50, 13), (50, 8), (50, 9),
    (51, 5), (51, 34), (51, 1),
    (52, 13), (52, 8),
    (53, 30), (53, 9), (53, 5), (53, 1),
    -- Dark Horse
    (54, 1), (54, 2), (54, 14),
    (55, 3), (55, 4),
    (56, 13), (56, 30),
    (57, 1), (57, 2),
    (58, 24), (58, 26),
    -- Image
    (59, 13), (59, 30), (59, 14),
    (60, 1), (60, 5), (60, 2),
    (61, 1), (61, 2), (61, 29),
    (62, 15), (62, 35),
    (63, 1), (63, 24),
    (64, 1), (64, 2);
