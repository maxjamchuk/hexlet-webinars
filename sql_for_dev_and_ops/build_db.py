#!/usr/bin/env python3
"""build_db.py - build the educational ``superheroes.sqlite`` database.

What this script does, in order:

1. Create a fresh ``superheroes.sqlite`` file (any old one is deleted).
2. Turn on foreign keys and create every table + index from ``schema.sql``.
3. Insert a curated CORE of well-known characters (commonly-known facts only:
   names, publisher, team, first appearance year, city, powers). This guarantees
   that recognisable characters are always present for the webinar.
4. Fetch ADDITIONAL real characters from open, machine-readable sources to add
   volume:
     * FIRST choice: Wikidata (SPARQL query service).
     * If Wikidata is unavailable, DBpedia (also open data from Wikipedia).
   Comic series/titles are filtered out; powers and first-appearance years are
   mined from the characters' own Wikipedia categories.
5. If BOTH internet sources fail (or ``requests`` is not installed), load the
   offline dataset from ``seed_manual_fallback.sql`` and print a warning.
6. Print row counts for every table and run validation queries, including
   ``PRAGMA foreign_key_check``.

Only two dependencies are used: ``requests`` (for the HTTP calls) and the
standard-library ``sqlite3`` module. ``requests`` is optional - without it the
script builds from the offline fallback.

DATA HONESTY
------------
* Names, publisher, team, first appearance year and city are factual.
* ``power_level`` is an ARTIFICIAL teaching value (1-100), derived deterministically
  from popularity + number of powers. It is NOT canon.
* ``is_active`` is a simplified teaching flag.
* Unknown fields are stored as NULL - nothing is invented.
* The curated core uses only short, commonly-known facts (no copied text).
"""

from __future__ import annotations

import re
import sqlite3
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:  # requests is optional; without it we use the fallback seed.
    requests = None  # type: ignore

# ---------------------------------------------------------------------------
# Paths and tunables
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "superheroes.sqlite"
SCHEMA_PATH = BASE_DIR / "schema.sql"
SEED_PATH = BASE_DIR / "seed_manual_fallback.sql"

MAX_HEROES = 1000        # hard cap on total heroes
PREFERRED_HEROES = 500   # nice-to-have target
MIN_HEROES = 300         # minimum "good" result
LIVE_CAP_PER_PUBLISHER = 160  # keeps the publisher mix balanced for GROUP BY demos

WDQS_ENDPOINT = "https://query.wikidata.org/sparql"
DBPEDIA_ENDPOINT = "https://dbpedia.org/sparql"
USER_AGENT = "SuperheroesWebinarDB/1.0 (educational SQL basics demo; contact: instructor@example.com)"

# Canonical publishers and their factual details.
PUBLISHER_INFO = {
    "Marvel Comics":     (1939, "United States", "https://www.wikidata.org/wiki/Q173496"),
    "DC Comics":         (1934, "United States", "https://www.wikidata.org/wiki/Q2924461"),
    "Dark Horse Comics": (1986, "United States", "https://www.wikidata.org/wiki/Q373933"),
    "Image Comics":      (1992, "United States", "https://www.wikidata.org/wiki/Q913301"),
}

# Wikidata publisher QIDs -> canonical names.
PUBLISHER_QID_TO_NAME = {
    "Q173496": "Marvel Comics", "Q931597": "Marvel Comics",
    "Q2924461": "DC Comics", "Q1152150": "DC Comics",
    "Q373933": "Dark Horse Comics", "Q140069695": "Dark Horse Comics",
    "Q913301": "Image Comics",
}

# DBpedia entry points per publisher: a set of Wikipedia character categories to
# pull members from, plus the publisher resource (dbo:publisher). Using several
# entry points per publisher gives us plenty of real characters to choose from.
DBPEDIA_ENTRY = {
    "Marvel Comics": {
        "resource": "Marvel_Comics",
        "categories": [
            "Marvel_Comics_male_superheroes", "Marvel_Comics_female_superheroes",
            "Marvel_Comics_supervillains", "Marvel_Comics_superheroes",
            "Marvel_Comics_antiheroes",
        ],
    },
    "DC Comics": {
        "resource": "DC_Comics",
        "categories": [
            "DC_Comics_male_superheroes", "DC_Comics_female_superheroes",
            "DC_Comics_supervillains", "DC_Comics_superheroes",
        ],
    },
    "Dark Horse Comics": {
        "resource": "Dark_Horse_Comics",
        "categories": [
            "Dark_Horse_Comics_superheroes", "Dark_Horse_Comics_characters",
            "Dark_Horse_Comics_supervillains",
        ],
    },
    "Image Comics": {
        "resource": "Image_Comics",
        "categories": [
            "Image_Comics_superheroes", "Image_Comics_supervillains",
            "Image_Comics_characters",
        ],
    },
}

# Known major teams -> the publisher they belong to (keeps the teams table clean).
KNOWN_TEAMS = {
    "Avengers": "Marvel Comics", "X-Men": "Marvel Comics", "X-Force": "Marvel Comics",
    "X-Factor": "Marvel Comics", "Fantastic Four": "Marvel Comics",
    "Guardians of the Galaxy": "Marvel Comics", "Defenders": "Marvel Comics",
    "Inhumans": "Marvel Comics", "Thunderbolts": "Marvel Comics",
    "Justice League": "DC Comics", "Justice Society": "DC Comics",
    "Teen Titans": "DC Comics", "Suicide Squad": "DC Comics",
    "Green Lantern Corps": "DC Comics", "Birds of Prey": "DC Comics",
    "Legion of Super-Heroes": "DC Comics",
    "B.P.R.D.": "Dark Horse Comics",
    "Youngblood": "Image Comics", "Cyberforce": "Image Comics",
}

# Optional base city / founded year for the known teams.
TEAM_INFO = {
    "Avengers": ("New York City", 1963),
    "X-Men": ("Salem Center", 1963),
    "Fantastic Four": ("New York City", 1961),
    "Guardians of the Galaxy": (None, 1969),
    "Justice League": (None, 1960),
    "Teen Titans": (None, 1964),
    "Suicide Squad": (None, 1959),
    "B.P.R.D.": ("Fairfield", None),
}

# The catalog of powers and their category (matches seed_manual_fallback.sql).
POWERS_CATALOG = [
    ("Superhuman Strength", "physical"), ("Superhuman Durability", "physical"),
    ("Superhuman Agility", "physical"), ("Enhanced Senses", "physical"),
    ("Flight", "movement"), ("Super Speed", "movement"),
    ("Wall-Crawling", "movement"), ("Teleportation", "movement"),
    ("Telepathy", "mental"), ("Telekinesis", "mental"),
    ("Mind Control", "mental"), ("Genius Intelligence", "mental"),
    ("Magic", "mystical"), ("Immortality", "mystical"),
    ("Energy Manipulation", "mystical"), ("Weather Control", "mystical"),
    ("Powered Armor", "technology"), ("Advanced Technology", "technology"),
    ("Utility Gadgets", "equipment"), ("Bow and Arrows", "equipment"),
    ("Shield", "equipment"), ("Hammer", "equipment"), ("Trident", "equipment"),
    ("Martial Arts", "skill"), ("Master Tactician", "skill"),
    ("Marksmanship", "skill"), ("Stealth", "skill"), ("Swordsmanship", "skill"),
    ("Healing Factor", "biological"), ("Shapeshifting", "biological"),
    ("Claws", "biological"), ("Toxin Immunity", "biological"),
    ("Cosmic Power", "cosmic"), ("Energy Projection", "cosmic"),
    ("Force Field", "cosmic"), ("Unknown", "unknown"),
]

# Wikipedia category substring -> power. Used to mine powers for live characters
# from their own "characters with X" categories.
CATEGORY_POWER_MAP = [
    ("superhuman_strength", "Superhuman Strength"),
    ("superhuman_speed", "Super Speed"),
    ("super_speed", "Super Speed"),
    ("superhuman_durability", "Superhuman Durability"),
    ("invulnerab", "Superhuman Durability"),
    ("accelerated_healing", "Healing Factor"),
    ("healing_factor", "Healing Factor"),
    ("superhuman_senses", "Enhanced Senses"),
    ("who_can_fly", "Flight"),
    ("characters_with_flight", "Flight"),
    ("telepath", "Telepathy"),
    ("telekinesis", "Telekinesis"),
    ("telekinetic", "Telekinesis"),
    ("energy_manipulation", "Energy Manipulation"),
    ("magic", "Magic"),
    ("sorcerer", "Magic"),
    ("witch", "Magic"),
    ("martial_artist", "Martial Arts"),
    ("swordfighter", "Swordsmanship"),
    ("swordsmen", "Swordsmanship"),
    ("archer", "Bow and Arrows"),
    ("marksmen", "Marksmanship"),
    ("shapeshifter", "Shapeshifting"),
    ("metamorph", "Shapeshifting"),
    ("teleport", "Teleportation"),
    ("weather", "Weather Control"),
    ("immortal", "Immortality"),
    ("scientist", "Genius Intelligence"),
    ("inventor", "Genius Intelligence"),
    ("spider_powers", "Wall-Crawling"),
    ("powered_armor", "Powered Armor"),
    ("powered_exoskeleton", "Powered Armor"),
]

# These curated core characters are marked inactive (simplified teaching flag).
INACTIVE_ALIASES = {"concrete", "barb wire", "shadowhawk", "the maxx"}

# ---------------------------------------------------------------------------
# Curated CORE of famous characters (commonly-known facts only).
# Fields: alias, real_name, publisher, team, alignment, year, city, [powers]
# ---------------------------------------------------------------------------
FAMOUS = [
    # Marvel Comics
    ("Spider-Man", "Peter Parker", "Marvel Comics", None, "hero", 1962, "New York City",
     ["Wall-Crawling", "Superhuman Strength", "Superhuman Agility", "Enhanced Senses"]),
    ("Iron Man", "Tony Stark", "Marvel Comics", "Avengers", "hero", 1963, "New York City",
     ["Powered Armor", "Flight", "Energy Projection", "Genius Intelligence"]),
    ("Captain America", "Steve Rogers", "Marvel Comics", "Avengers", "hero", 1941, "New York City",
     ["Superhuman Strength", "Superhuman Agility", "Shield", "Master Tactician"]),
    ("Thor", "Thor Odinson", "Marvel Comics", "Avengers", "hero", 1962, "Asgard",
     ["Superhuman Strength", "Flight", "Hammer", "Weather Control"]),
    ("Hulk", "Bruce Banner", "Marvel Comics", "Avengers", "hero", 1962, None,
     ["Superhuman Strength", "Superhuman Durability", "Healing Factor"]),
    ("Black Widow", "Natasha Romanoff", "Marvel Comics", "Avengers", "hero", 1964, None,
     ["Martial Arts", "Marksmanship", "Stealth"]),
    ("Hawkeye", "Clint Barton", "Marvel Comics", "Avengers", "hero", 1964, None,
     ["Bow and Arrows", "Marksmanship"]),
    ("Wolverine", "Logan", "Marvel Comics", "X-Men", "antihero", 1974, None,
     ["Claws", "Healing Factor", "Enhanced Senses"]),
    ("Cyclops", "Scott Summers", "Marvel Comics", "X-Men", "hero", 1963, None,
     ["Energy Projection"]),
    ("Storm", "Ororo Munroe", "Marvel Comics", "X-Men", "hero", 1975, None,
     ["Weather Control", "Flight"]),
    ("Jean Grey", "Jean Grey", "Marvel Comics", "X-Men", "hero", 1963, None,
     ["Telepathy", "Telekinesis"]),
    ("Professor X", "Charles Xavier", "Marvel Comics", "X-Men", "hero", 1963, "Salem Center",
     ["Telepathy", "Mind Control", "Genius Intelligence"]),
    ("Magneto", "Max Eisenhardt", "Marvel Comics", None, "villain", 1963, None,
     ["Energy Manipulation", "Flight", "Force Field"]),
    ("Deadpool", "Wade Wilson", "Marvel Comics", None, "antihero", 1991, "New York City",
     ["Healing Factor", "Martial Arts", "Swordsmanship"]),
    ("Doctor Strange", "Stephen Strange", "Marvel Comics", None, "hero", 1963, "New York City",
     ["Magic", "Teleportation", "Immortality"]),
    ("Black Panther", "T'Challa", "Marvel Comics", "Avengers", "hero", 1966, None,
     ["Superhuman Strength", "Superhuman Agility", "Martial Arts", "Enhanced Senses"]),
    ("Captain Marvel", "Carol Danvers", "Marvel Comics", "Avengers", "hero", 1968, None,
     ["Flight", "Superhuman Strength", "Energy Projection", "Cosmic Power"]),
    ("Scarlet Witch", "Wanda Maximoff", "Marvel Comics", "Avengers", "antihero", 1964, None,
     ["Magic", "Telekinesis"]),
    ("Vision", None, "Marvel Comics", "Avengers", "hero", 1968, None,
     ["Flight", "Shapeshifting", "Energy Projection", "Genius Intelligence"]),
    ("Mister Fantastic", "Reed Richards", "Marvel Comics", "Fantastic Four", "hero", 1961, "New York City",
     ["Shapeshifting", "Genius Intelligence"]),
    ("Invisible Woman", "Susan Storm", "Marvel Comics", "Fantastic Four", "hero", 1961, "New York City",
     ["Force Field"]),
    ("Human Torch", "Johnny Storm", "Marvel Comics", "Fantastic Four", "hero", 1961, "New York City",
     ["Flight", "Energy Projection"]),
    ("Thing", "Ben Grimm", "Marvel Comics", "Fantastic Four", "hero", 1961, "New York City",
     ["Superhuman Strength", "Superhuman Durability"]),
    ("Star-Lord", "Peter Quill", "Marvel Comics", "Guardians of the Galaxy", "hero", 1976, None,
     ["Marksmanship", "Flight"]),
    ("Gamora", None, "Marvel Comics", "Guardians of the Galaxy", "antihero", 1975, None,
     ["Martial Arts", "Swordsmanship", "Superhuman Strength"]),
    ("Groot", None, "Marvel Comics", "Guardians of the Galaxy", "hero", 1960, None,
     ["Superhuman Strength", "Shapeshifting", "Superhuman Durability"]),
    ("Rocket Raccoon", None, "Marvel Comics", "Guardians of the Galaxy", "hero", 1976, None,
     ["Marksmanship", "Genius Intelligence", "Advanced Technology"]),
    ("Venom", "Eddie Brock", "Marvel Comics", None, "antihero", 1988, "New York City",
     ["Superhuman Strength", "Wall-Crawling", "Shapeshifting"]),
    ("Green Goblin", "Norman Osborn", "Marvel Comics", None, "villain", 1964, "New York City",
     ["Flight", "Superhuman Strength", "Genius Intelligence", "Advanced Technology"]),
    ("Thanos", None, "Marvel Comics", None, "villain", 1973, None,
     ["Superhuman Strength", "Superhuman Durability", "Cosmic Power", "Energy Manipulation"]),
    ("Silver Surfer", "Norrin Radd", "Marvel Comics", None, "hero", 1966, None,
     ["Flight", "Cosmic Power", "Energy Projection"]),
    ("Daredevil", "Matt Murdock", "Marvel Comics", None, "hero", 1964, "New York City",
     ["Enhanced Senses", "Martial Arts", "Superhuman Agility"]),
    # DC Comics
    ("Superman", "Clark Kent", "DC Comics", "Justice League", "hero", 1938, "Metropolis",
     ["Superhuman Strength", "Flight", "Energy Projection", "Superhuman Durability"]),
    ("Batman", "Bruce Wayne", "DC Comics", "Justice League", "hero", 1939, "Gotham City",
     ["Martial Arts", "Master Tactician", "Utility Gadgets", "Genius Intelligence"]),
    ("Wonder Woman", "Diana Prince", "DC Comics", "Justice League", "hero", 1941, "Themyscira",
     ["Superhuman Strength", "Flight", "Swordsmanship", "Martial Arts"]),
    ("The Flash", "Barry Allen", "DC Comics", "Justice League", "hero", 1956, "Central City",
     ["Super Speed"]),
    ("Green Lantern", "Hal Jordan", "DC Comics", "Justice League", "hero", 1959, "Coast City",
     ["Energy Manipulation", "Flight", "Force Field"]),
    ("Aquaman", "Arthur Curry", "DC Comics", "Justice League", "hero", 1941, "Atlantis",
     ["Superhuman Strength", "Trident", "Mind Control"]),
    ("Cyborg", "Victor Stone", "DC Comics", "Justice League", "hero", 1980, None,
     ["Advanced Technology", "Energy Projection", "Genius Intelligence"]),
    ("Green Arrow", "Oliver Queen", "DC Comics", None, "hero", 1941, "Star City",
     ["Bow and Arrows", "Marksmanship", "Martial Arts"]),
    ("Shazam", "Billy Batson", "DC Comics", None, "hero", 1940, None,
     ["Superhuman Strength", "Flight", "Super Speed", "Magic"]),
    ("Nightwing", "Dick Grayson", "DC Comics", "Teen Titans", "hero", 1940, "Bludhaven",
     ["Martial Arts", "Superhuman Agility", "Master Tactician"]),
    ("Batgirl", "Barbara Gordon", "DC Comics", None, "hero", 1967, "Gotham City",
     ["Martial Arts", "Genius Intelligence", "Utility Gadgets"]),
    ("Supergirl", "Kara Zor-El", "DC Comics", None, "hero", 1959, "Metropolis",
     ["Superhuman Strength", "Flight", "Energy Projection", "Superhuman Durability"]),
    ("Harley Quinn", "Harleen Quinzel", "DC Comics", "Suicide Squad", "antihero", 1992, "Gotham City",
     ["Martial Arts", "Superhuman Agility", "Toxin Immunity"]),
    ("Joker", None, "DC Comics", None, "villain", 1940, "Gotham City",
     ["Master Tactician", "Toxin Immunity"]),
    ("Lex Luthor", "Lex Luthor", "DC Comics", None, "villain", 1940, "Metropolis",
     ["Genius Intelligence", "Advanced Technology", "Powered Armor"]),
    ("Catwoman", "Selina Kyle", "DC Comics", None, "antihero", 1940, "Gotham City",
     ["Martial Arts", "Superhuman Agility", "Stealth"]),
    ("Deathstroke", "Slade Wilson", "DC Comics", None, "villain", 1980, None,
     ["Superhuman Strength", "Martial Arts", "Swordsmanship", "Healing Factor"]),
    ("Raven", "Rachel Roth", "DC Comics", "Teen Titans", "hero", 1980, None,
     ["Magic", "Teleportation", "Telepathy"]),
    ("Starfire", "Koriand'r", "DC Comics", "Teen Titans", "hero", 1980, None,
     ["Flight", "Energy Projection", "Superhuman Strength"]),
    ("Zatanna", "Zatanna Zatara", "DC Comics", None, "hero", 1964, None,
     ["Magic", "Teleportation"]),
    ("Martian Manhunter", "J'onn J'onzz", "DC Comics", "Justice League", "hero", 1955, None,
     ["Shapeshifting", "Telepathy", "Flight", "Superhuman Strength"]),
    # Dark Horse Comics
    ("Hellboy", "Anung un Rama", "Dark Horse Comics", "B.P.R.D.", "antihero", 1993, None,
     ["Superhuman Strength", "Superhuman Durability", "Immortality"]),
    ("Abe Sapien", "Abraham Sapien", "Dark Horse Comics", "B.P.R.D.", "hero", 1994, None,
     ["Superhuman Agility", "Enhanced Senses"]),
    ("The Mask", "Stanley Ipkiss", "Dark Horse Comics", None, "antihero", 1987, None,
     ["Magic", "Shapeshifting"]),
    ("Concrete", "Ronald Lithgow", "Dark Horse Comics", None, "hero", 1986, None,
     ["Superhuman Strength", "Superhuman Durability"]),
    ("Barb Wire", "Barbara Kopetski", "Dark Horse Comics", None, "antihero", 1994, None,
     ["Martial Arts", "Marksmanship"]),
    # Image Comics
    ("Spawn", "Al Simmons", "Image Comics", None, "antihero", 1992, "New York City",
     ["Magic", "Shapeshifting", "Immortality"]),
    ("Invincible", "Mark Grayson", "Image Comics", None, "hero", 2003, None,
     ["Superhuman Strength", "Flight", "Superhuman Durability"]),
    ("Savage Dragon", None, "Image Comics", None, "hero", 1992, "Chicago",
     ["Superhuman Strength", "Superhuman Durability", "Healing Factor"]),
    ("Witchblade", "Sara Pezzini", "Image Comics", None, "hero", 1995, "New York City",
     ["Energy Manipulation", "Force Field"]),
    ("Shadowhawk", "Paul Johnstone", "Image Comics", None, "antihero", 1992, None,
     ["Superhuman Strength", "Martial Arts"]),
    ("The Maxx", None, "Image Comics", None, "hero", 1993, None,
     ["Superhuman Strength", "Superhuman Durability"]),
]

# --- Wikidata SPARQL: one query for all four publishers -------------------
SPARQL_QUERY = """
SELECT ?c ?cLabel ?pub ?inception ?sitelinks
       (GROUP_CONCAT(DISTINCT ?typeLabel; separator="|") AS ?types)
       (SAMPLE(?teamLabel) AS ?team)
WHERE {
  {
    VALUES ?pub { wd:Q173496 wd:Q2924461 wd:Q373933 wd:Q140069695 wd:Q913301 }
    ?c wdt:P123 ?pub .
  }
  UNION
  {
    VALUES ?uni { wd:Q931597 wd:Q1152150 }
    ?c wdt:P1080 ?uni .
    BIND(?uni AS ?pub)
  }
  ?c wikibase:sitelinks ?sitelinks .
  ?c rdfs:label ?cLabel . FILTER(LANG(?cLabel) = "en")
  OPTIONAL { ?c wdt:P571 ?inception . }
  OPTIONAL { ?c wdt:P31 ?type . ?type rdfs:label ?typeLabel . FILTER(LANG(?typeLabel) = "en") }
  OPTIONAL { ?c wdt:P463 ?teamItem . ?teamItem rdfs:label ?teamLabel . FILTER(LANG(?teamLabel) = "en") }
}
GROUP BY ?c ?cLabel ?pub ?inception ?sitelinks
ORDER BY DESC(?sitelinks)
LIMIT 1500
"""

# --- DBpedia SPARQL: one lighter query per entry point ---------------------
# The DBpedia public endpoint has a server-side time limit. A single big query
# that UNIONs several large categories can exceed it (HTTP 206 partial). So we
# query ONE entry point at a time (a category, or the publisher link) and merge
# the results in Python. Each query is small and reliable.
def build_dbpedia_entry_query(kind: str, value: str) -> str:
    """Build a query for a single entry point.

    kind is either 'category' (members of a Wikipedia category) or
    'publisher' (items linked with dbo:publisher).

    The query is kept deliberately light: it aggregates only the character's
    own subject categories (used to mine powers, first-appearance year and
    alignment). We do NOT also aggregate alliances here, because combining two
    GROUP_CONCATs multiplies the intermediate rows and makes the public DBpedia
    endpoint time out (HTTP 206). Team links come from the curated core instead.
    """
    if kind == "category":
        selector = f"?c dct:subject dbc:{value} ."
    else:
        selector = f"?c dbo:publisher dbr:{value} ."
    return f"""
SELECT ?c ?name (SAMPLE(?debutRaw) AS ?debut) (SAMPLE(?alterRaw) AS ?alter)
       (GROUP_CONCAT(DISTINCT ?subjLocal; separator="|") AS ?subjects)
WHERE {{
  {selector}
  ?c rdfs:label ?name . FILTER(LANG(?name) = "en")
  FILTER NOT EXISTS {{ ?c dbo:wikiPageRedirects ?anyRedirect . }}
  OPTIONAL {{ ?c dbp:debut ?debutRaw . }}
  OPTIONAL {{ ?c dbp:alterEgo ?alterRaw . }}
  OPTIONAL {{ ?c dct:subject ?subj . BIND(REPLACE(STR(?subj), ".*/Category:", "") AS ?subjLocal) }}
}}
GROUP BY ?c ?name
LIMIT 400
"""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def qid_from_uri(uri: str) -> str:
    return uri.rsplit("/", 1)[-1]


def clean_alias(name: str) -> str:
    """Drop a trailing '(disambiguation)' suffix: 'Vision (Marvel Comics)' -> 'Vision'."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()


def clean_real_name(value: str | None) -> str | None:
    """Keep a source-provided real name only if it looks like a plain name."""
    if not value:
        return None
    v = value.strip()
    if not v or len(v) > 45 or any(ch in v for ch in "[]{}<>|\n"):
        return None
    if v.count(",") > 1 or not any(ch.isalpha() for ch in v):
        return None
    return v


def parse_year(value: str | None) -> int | None:
    if not value:
        return None
    match = re.search(r"(18|19|20)\d{2}", value)
    if not match:
        return None
    year = int(match.group(0))
    return year if 1800 <= year <= date.today().year else None


def infer_alignment(text: str) -> str:
    t = text.lower()
    if "anti-hero" in t or "antihero" in t:
        return "antihero"
    if "supervillain" in t or "villain" in t:
        return "villain"
    if "superhero" in t or "superheroine" in t:
        return "hero"
    return "unknown"


def mine_powers(subjects_lower: str) -> list[str]:
    """Read powers from a character's own Wikipedia categories."""
    found: list[str] = []
    for needle, power in CATEGORY_POWER_MAP:
        if needle in subjects_lower and power not in found:
            found.append(power)
    return found[:4]


def looks_like_character(subjects_lower: str, debut: str | None, alter: str | None, name: str) -> bool:
    """Heuristic to keep real characters and drop series/titles/list pages."""
    low = name.lower()
    if low.startswith(("list of", "alternative versions", "alternative version")):
        return False
    if "(disambiguation)" in low:
        return False
    # An aggregate/list page tends to carry several different introduction years.
    if len(set(re.findall(r"introduced_in_(\d{4})", subjects_lower))) > 1:
        return False
    if debut or alter:
        return True
    signals = ("superheroes", "supervillains", "antiheroes", "heroines",
               "villainesses", "_characters_", "mutants", "deities")
    if any(s in subjects_lower for s in signals):
        return True
    return bool(mine_powers(subjects_lower))


def match_known_team(candidates: list[str], publisher: str) -> str | None:
    for candidate in candidates:
        low = candidate.lower()
        for team, team_publisher in KNOWN_TEAMS.items():
            if team_publisher == publisher and team.lower() in low:
                return team
    return None


def derive_power_level(popularity: float, num_powers: int) -> int:
    """Artificial 1-100 teaching value from popularity (0..1) + number of powers."""
    popularity = max(0.0, min(1.0, popularity))
    score = 15 + popularity * 60 + min(num_powers, 6) / 6 * 25
    return max(1, min(100, round(score)))


def today_iso() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Database creation
# ---------------------------------------------------------------------------
def create_database() -> sqlite3.Connection:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return conn


# ---------------------------------------------------------------------------
# Live source 1: Wikidata
# ---------------------------------------------------------------------------
def fetch_wikidata(max_attempts: int = 3) -> list[dict] | None:
    if requests is None:
        return None
    headers = {"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"}
    params = {"query": SPARQL_QUERY, "format": "json"}
    for attempt in range(1, max_attempts + 1):
        print(f"  Wikidata attempt {attempt}/{max_attempts} ...")
        last = attempt == max_attempts
        try:
            resp = requests.get(WDQS_ENDPOINT, params=params, headers=headers, timeout=(10, 40))
        except requests.RequestException as exc:
            print(f"    network error: {exc}")
            if not last:
                time.sleep(8)
            continue
        if resp.status_code == 200:
            try:
                bindings = resp.json()["results"]["bindings"]
            except (ValueError, KeyError) as exc:
                print(f"    could not parse response: {exc}")
                return None
            rows = [r for r in (parse_wikidata_row(b) for b in bindings) if r]
            print(f"    received {len(rows)} usable rows.")
            return rows
        if resp.status_code == 429:
            if last:
                print("    rate limited (429); giving up on Wikidata.")
                break
            wait = min(max(int(resp.headers.get("Retry-After", "60") or "60"), 30), 75)
            print(f"    rate limited (429); waiting {wait}s ...")
            time.sleep(wait)
            continue
        if resp.status_code in (500, 502, 503, 504):
            if last:
                break
            print(f"    server error {resp.status_code}; waiting 12s ...")
            time.sleep(12)
            continue
        print(f"    unexpected status {resp.status_code}; giving up on Wikidata.")
        return None
    print("    exhausted all Wikidata attempts.")
    return None


def parse_wikidata_row(b: dict) -> dict | None:
    alias = b.get("cLabel", {}).get("value")
    if not alias:
        return None
    publisher = PUBLISHER_QID_TO_NAME.get(qid_from_uri(b["pub"]["value"]))
    if not publisher:
        return None
    sitelinks = int(b.get("sitelinks", {}).get("value", 0) or 0)
    team_label = b.get("team", {}).get("value")
    qid = qid_from_uri(b["c"]["value"])
    return {
        "qid": qid,
        "alias": clean_alias(alias),
        "publisher": publisher,
        "year": parse_year(b.get("inception", {}).get("value")),
        "alignment": infer_alignment(b.get("types", {}).get("value", "")),
        "team": match_known_team([team_label], publisher) if team_label else None,
        "real_name": None,
        "powers": [],
        "popularity": min(sitelinks, 120) / 120,
        "source_name": "Wikidata",
        "source_url": f"https://www.wikidata.org/wiki/{qid}",
    }


# ---------------------------------------------------------------------------
# Live source 2: DBpedia
# ---------------------------------------------------------------------------
def dbpedia_run(query: str, headers: dict, attempts: int = 2) -> list[dict] | None:
    """Run one DBpedia query, retrying once on a partial/timeout (HTTP 206)."""
    for attempt in range(1, attempts + 1):
        try:
            resp = requests.get(
                DBPEDIA_ENDPOINT,
                params={"query": query, "format": "application/sparql-results+json"},
                headers=headers,
                timeout=(10, 60),
            )
        except requests.RequestException as exc:
            print(f"      network error: {exc}")
            if attempt < attempts:
                time.sleep(5)
            continue
        if resp.status_code == 200:
            try:
                return resp.json()["results"]["bindings"]
            except (ValueError, KeyError) as exc:
                print(f"      could not parse response: {exc}")
                return None
        if resp.status_code == 206 and attempt < attempts:
            print("      partial result (206); retrying once ...")
            time.sleep(5)
            continue
        print(f"      status {resp.status_code}.")
        return None
    return None


def fetch_dbpedia() -> list[dict] | None:
    if requests is None:
        return None
    headers = {"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"}
    all_rows: list[dict] = []
    for publisher, entry in DBPEDIA_ENTRY.items():
        print(f"  DBpedia queries for {publisher} ...")
        # One entry point at a time, dedup by DBpedia resource URI.
        entry_points = [("category", cat) for cat in entry["categories"]]
        entry_points.append(("publisher", entry["resource"]))
        by_uri: dict[str, dict] = {}
        for kind, value in entry_points:
            bindings = dbpedia_run(build_dbpedia_entry_query(kind, value), headers)
            if not bindings:
                continue
            for b in bindings:
                uri = b.get("c", {}).get("value")
                if not uri or uri in by_uri:
                    continue
                row = parse_dbpedia_row(b, publisher)
                if row:
                    by_uri[uri] = row
            time.sleep(1)  # be polite between requests
        rows = sorted(by_uri.values(), key=lambda r: r["popularity"], reverse=True)
        rows = rows[:LIVE_CAP_PER_PUBLISHER]
        print(f"    {publisher}: {len(rows)} characters kept.")
        all_rows.extend(rows)
    return all_rows or None


def parse_dbpedia_row(b: dict, publisher: str) -> dict | None:
    raw_name = b.get("name", {}).get("value", "")
    alias = clean_alias(raw_name)
    if not alias:
        return None
    subjects = b.get("subjects", {}).get("value", "")
    subjects_lower = subjects.lower()
    debut = b.get("debut", {}).get("value")
    alter = b.get("alter", {}).get("value")
    if not looks_like_character(subjects_lower, debut, alter, raw_name):
        return None
    year_match = re.search(r"introduced_in_(\d{4})", subjects_lower)
    year = int(year_match.group(1)) if year_match else parse_year(debut)
    num_subjects = len([s for s in subjects.split("|") if s])
    return {
        "qid": None,
        "alias": alias,
        "publisher": publisher,
        "year": year,
        "alignment": infer_alignment(subjects_lower),
        "team": None,  # live team links are not fetched; teams come from the curated core
        "real_name": clean_real_name(alter),
        "powers": mine_powers(subjects_lower),
        "popularity": min(num_subjects, 30) / 30,
        "source_name": "DBpedia",
        "source_url": b.get("c", {}).get("value"),
    }


# ---------------------------------------------------------------------------
# Insert helpers
# ---------------------------------------------------------------------------
def insert_publishers(cur: sqlite3.Cursor) -> dict[str, int]:
    for name, (founded, country, url) in PUBLISHER_INFO.items():
        cur.execute(
            "INSERT OR IGNORE INTO publishers (name, founded_year, country, source_url) VALUES (?, ?, ?, ?)",
            (name, founded, country, url),
        )
    return {name: cur.execute("SELECT id FROM publishers WHERE name = ?", (name,)).fetchone()[0]
            for name in PUBLISHER_INFO}


def insert_powers(cur: sqlite3.Cursor) -> dict[str, int]:
    for name, category in POWERS_CATALOG:
        cur.execute("INSERT OR IGNORE INTO powers (name, category) VALUES (?, ?)", (name, category))
    return {name: cur.execute("SELECT id FROM powers WHERE name = ?", (name,)).fetchone()[0]
            for name, _ in POWERS_CATALOG}


def build_online(conn: sqlite3.Connection, live_rows: list[dict]) -> int:
    """Insert the curated famous core plus deduplicated live rows."""
    cur = conn.cursor()
    publisher_ids = insert_publishers(cur)
    power_ids = insert_powers(cur)
    team_ids: dict[tuple[str, int], int] = {}

    def team_id_for(name: str | None, publisher_id: int) -> int | None:
        if not name:
            return None
        key = (name, publisher_id)
        if key not in team_ids:
            base_city, founded = TEAM_INFO.get(name, (None, None))
            cur.execute(
                "INSERT OR IGNORE INTO teams (name, publisher_id, base_city, founded_year) VALUES (?, ?, ?, ?)",
                (name, publisher_id, base_city, founded),
            )
            team_ids[key] = cur.execute(
                "SELECT id FROM teams WHERE name = ? AND publisher_id = ?", key
            ).fetchone()[0]
        return team_ids[key]

    def add_powers(hero_id: int, powers: list[str]) -> None:
        for power_name in powers:
            power_id = power_ids.get(power_name)
            if power_id:
                cur.execute(
                    "INSERT OR IGNORE INTO hero_powers (hero_id, power_id) VALUES (?, ?)",
                    (hero_id, power_id),
                )

    seen_alias_pub: set[tuple[str, str]] = set()
    seen_qid: set[str] = set()
    sources: list[tuple[int, str, str | None]] = []

    # 1) Curated famous core.
    for alias, real_name, publisher, team, alignment, year, city, powers in FAMOUS:
        publisher_id = publisher_ids[publisher]
        is_active = 0 if alias.lower() in INACTIVE_ALIASES else 1
        power_level = derive_power_level(0.85, len(powers))
        cur.execute(
            """INSERT INTO heroes
                 (alias, real_name, publisher_id, team_id, alignment,
                  first_appearance_year, city, power_level, is_active, wikidata_qid, source_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)""",
            (alias, real_name, publisher_id, team_id_for(team, publisher_id),
             alignment, year, city, power_level, is_active),
        )
        hero_id = cur.lastrowid
        add_powers(hero_id, powers)
        seen_alias_pub.add((alias.lower(), publisher))
        sources.append((hero_id, "curated (commonly-known facts)", None))

    # 2) Live rows for additional volume.
    for row in live_rows:
        if len(seen_alias_pub) >= MAX_HEROES:
            break
        if row["qid"] and row["qid"] in seen_qid:
            continue
        key = (row["alias"].lower(), row["publisher"])
        if key in seen_alias_pub:
            continue
        seen_alias_pub.add(key)
        if row["qid"]:
            seen_qid.add(row["qid"])

        publisher_id = publisher_ids[row["publisher"]]
        power_level = derive_power_level(row["popularity"], len(row["powers"]))
        cur.execute(
            """INSERT INTO heroes
                 (alias, real_name, publisher_id, team_id, alignment,
                  first_appearance_year, city, power_level, is_active, wikidata_qid, source_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)""",
            (row["alias"], row["real_name"], publisher_id,
             team_id_for(row["team"], publisher_id), row["alignment"],
             row["year"], None, power_level, row["qid"], row["source_url"]),
        )
        hero_id = cur.lastrowid
        add_powers(hero_id, row["powers"])
        sources.append((hero_id, row["source_name"], row["source_url"]))

    # 3) Provenance records.
    retrieved = today_iso()
    for name, publisher_id in publisher_ids.items():
        cur.execute(
            "INSERT INTO sources (entity_type, entity_id, source_name, source_url, retrieved_at) VALUES ('publisher', ?, ?, ?, ?)",
            (publisher_id, "Wikidata", PUBLISHER_INFO[name][2], retrieved),
        )
    for hero_id, source_name, url in sources:
        cur.execute(
            "INSERT INTO sources (entity_type, entity_id, source_name, source_url, retrieved_at) VALUES ('hero', ?, ?, ?, ?)",
            (hero_id, source_name, url, retrieved),
        )

    conn.commit()
    return len(seen_alias_pub)


def build_fallback(conn: sqlite3.Connection) -> int:
    conn.executescript(SEED_PATH.read_text(encoding="utf-8"))
    cur = conn.cursor()
    retrieved = today_iso()
    for (publisher_id,) in cur.execute("SELECT id FROM publishers").fetchall():
        cur.execute(
            "INSERT INTO sources (entity_type, entity_id, source_name, source_url, retrieved_at) VALUES ('publisher', ?, ?, ?, ?)",
            (publisher_id, "manual fallback seed", None, retrieved),
        )
    for (hero_id,) in cur.execute("SELECT id FROM heroes").fetchall():
        cur.execute(
            "INSERT INTO sources (entity_type, entity_id, source_name, source_url, retrieved_at) VALUES ('hero', ?, ?, ?, ?)",
            (hero_id, "manual fallback seed", None, retrieved),
        )
    conn.commit()
    return cur.execute("SELECT COUNT(*) FROM heroes").fetchone()[0]


# ---------------------------------------------------------------------------
# Reporting and validation
# ---------------------------------------------------------------------------
def print_counts(conn: sqlite3.Connection) -> None:
    print("\nRow counts:")
    for table in ("publishers", "teams", "heroes", "powers", "hero_powers", "sources"):
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:<12} {count}")


def validate(conn: sqlite3.Connection) -> None:
    print("\nValidation:")
    per_publisher = conn.execute(
        """SELECT p.name, COUNT(*)
             FROM heroes h JOIN publishers p ON p.id = h.publisher_id
            GROUP BY p.name ORDER BY COUNT(*) DESC"""
    ).fetchall()
    print("  heroes per publisher:")
    for name, count in per_publisher:
        print(f"    {name:<20} {count}")
    without_team = conn.execute("SELECT COUNT(*) FROM heroes WHERE team_id IS NULL").fetchone()[0]
    print(f"  heroes without a team: {without_team}")
    without_powers = conn.execute(
        "SELECT COUNT(*) FROM heroes WHERE id NOT IN (SELECT hero_id FROM hero_powers)"
    ).fetchone()[0]
    print(f"  heroes without any power: {without_powers}")
    fk_problems = conn.execute("PRAGMA foreign_key_check").fetchall()
    if fk_problems:
        print(f"  FOREIGN KEY PROBLEMS FOUND: {fk_problems}")
    else:
        print("  foreign key check: OK (no problems)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    print(f"Building {DB_PATH.name} ...")
    conn = create_database()

    live_rows: list[dict] = []
    source_used = None
    if requests is not None:
        print("Trying Wikidata (preferred source) ...")
        rows = fetch_wikidata()
        if rows:
            live_rows, source_used = rows, "Wikidata"
        else:
            print("Wikidata unavailable; trying DBpedia ...")
            rows = fetch_dbpedia()
            if rows:
                live_rows, source_used = rows, "DBpedia"

    if source_used:
        hero_count = build_online(conn, live_rows)
        print(f"\nBuilt database: {len(FAMOUS)} curated core + live volume from {source_used} "
              f"= {hero_count} heroes total.")
        if hero_count < MIN_HEROES:
            print(f"WARNING: {hero_count} heroes is below the {MIN_HEROES} minimum target "
                  f"(kept the valid subset).")
        elif hero_count < PREFERRED_HEROES:
            print(f"NOTE: {hero_count} heroes (below the preferred {PREFERRED_HEROES}, but acceptable).")
    else:
        if requests is None:
            print("\n'requests' is not installed - using the offline fallback dataset.")
        else:
            print("\nCould not fetch live data - using the offline fallback dataset.")
        hero_count = build_fallback(conn)
        print(f"Loaded {hero_count} heroes from seed_manual_fallback.sql.")
        print("WARNING: this is the small offline teaching dataset, not the full live set.")

    print_counts(conn)
    validate(conn)
    conn.close()
    print(f"\nDone. Database written to {DB_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
