# Superheroes SQLite Database — SQL Basics Webinar

A small, self-contained project that builds a local SQLite database of real comic
book characters. It is designed for teaching the **basics of SQL**: `SELECT`,
`WHERE`, `ORDER BY`, `LIMIT`, `INSERT`, `UPDATE`, `DELETE`, `FOREIGN KEY`,
`INNER JOIN`, `LEFT JOIN`, `COUNT`, and `GROUP BY`.

The data is collected from **open, machine-readable sources** (Wikidata and, as a
fallback, DBpedia). Only short factual fields are stored — no long descriptions,
biographies, or plot summaries.

---

## Files

| File | What it is |
|------|------------|
| `build_db.py` | Python script that creates and fills `superheroes.sqlite`. |
| `schema.sql` | All `CREATE TABLE` / `CREATE INDEX` statements. |
| `seed_manual_fallback.sql` | Offline dataset (~60 famous characters), used only if the internet fetch fails. |
| `examples.sql` | Ready-to-run teaching queries, grouped by topic. |
| `superheroes.sqlite` | The generated database (created by `build_db.py`). |
| `README.md` | This file. |

---

## Requirements

- **Python 3.11+**
- **`requests`** (only for live data fetching)
- **`sqlite3`** — part of the Python standard library, nothing to install
- The **`sqlite3` command-line tool** is handy for exploring the database
  (on Debian/Ubuntu: `sudo apt install sqlite3`).

Install the one third-party dependency:

```bash
pip install requests
```

---

## How to build the database

From this folder:

```bash
python build_db.py
```

The script will:

1. Create a fresh `superheroes.sqlite` (any existing one is replaced).
2. Enable foreign keys and create all tables and indexes from `schema.sql`.
3. Insert a small **curated core** of famous characters (Spider-Man, Batman,
   Superman, Hellboy, Spawn, …) using only short, commonly-known facts. This
   guarantees the recognisable names are always present, with real names, teams
   and powers filled in.
4. Fetch **additional** real characters to add volume:
   - **Wikidata** is tried first (open, machine-readable).
   - If Wikidata is unavailable, **DBpedia** is used (also open data, extracted
     from Wikipedia). Comic series/titles are filtered out, and each character's
     powers and first-appearance year are read from their own Wikipedia
     categories.
5. If both live sources are unreachable, load the offline
   `seed_manual_fallback.sql` (about 60 well-known characters) and print a
   warning.
6. Print row counts and run validation checks (including
   `PRAGMA foreign_key_check`).

> The script targets up to 1000 heroes (preferred ~500, minimum ~300). A typical
> live run produces roughly 400 heroes across the four publishers. If fewer are
> available from reliable sources, it keeps the valid subset and warns you.

Because the extra characters come from live open data, the exact contents differ
a little from run to run — which is itself a realistic talking point about real
datasets.

---

## How to open and explore the database

```bash
sqlite3 superheroes.sqlite
```

Some helpful settings once you are inside the `sqlite3` prompt:

```sql
.headers on      -- show column names
.mode column     -- align output in columns
.tables          -- list all tables
.schema heroes   -- show the CREATE statement for a table
SELECT * FROM heroes LIMIT 5;
.quit            -- leave
```

## How to run the example queries

Run the whole teaching file at once:

```bash
sqlite3 superheroes.sqlite ".read examples.sql"
```

For a webinar it is better to open the database and paste the queries **one at a
time** so students can see each result. Open `examples.sql` in your editor and
copy queries as you go.

---

## What each table means

- **publishers** — the comic companies (Marvel, DC, Dark Horse, Image).
- **teams** — super teams (Avengers, X-Men, Justice League, …). Each team belongs
  to one publisher.
- **heroes** — the main table: one row per character, with a link to its publisher
  and (optionally) a team.
- **powers** — a catalog of abilities, each with a category (physical, mental,
  movement, mystical, technology, equipment, skill, biological, cosmic, unknown).
- **hero_powers** — the many-to-many link between heroes and powers.
- **sources** — provenance: where each publisher/hero row came from and when.

### The `heroes` columns

| Column | Meaning |
|--------|---------|
| `id` | Primary key. |
| `alias` | Public/hero name (e.g., *Spider-Man*). |
| `real_name` | Secret identity, when commonly known (else `NULL`). |
| `publisher_id` | Required link to `publishers`. |
| `team_id` | Optional link to `teams` (`NULL` if none). |
| `alignment` | One of `hero`, `antihero`, `villain`, `unknown`. |
| `first_appearance_year` | Year of first appearance, when known (else `NULL`). |
| `city` | Home city, when known (else `NULL`). |
| `power_level` | Artificial teaching value, 1–100 (see below). |
| `is_active` | Simplified teaching flag: `1` = active, `0` = not (see below). |
| `wikidata_qid` | Wikidata identifier, when available (unique). |
| `source_url` | Link to the source record. |

---

## Which fields are factual, and which are for teaching only

**Factual** (collected from open sources or commonly-known facts):
`alias`, `real_name`, `publisher`, `team`, `first_appearance_year`, `city`,
`alignment`, `wikidata_qid`, `source_url`, and the list of `powers`.

**Artificial / teaching-only:**

- **`power_level`** is **NOT canon.** There is no official, comparable "power
  level" for comic characters. This project generates a deterministic number
  from 1–100 based on how well-known a character is (how many Wikipedia language
  editions or categories mention them) plus how many powers we recorded. It exists
  purely so students have a numeric column to practice `ORDER BY`, `>=`, `AVG`,
  etc. Treat it as a game stat, not a fact.
- **`is_active`** is a **simplified flag** for teaching `WHERE` and `UPDATE`. Live
  data defaults everyone to `1`; the offline dataset marks a few legacy characters
  as `0`. It is not a precise statement about current comic continuity.

When a factual field is unknown, it is stored as `NULL` — nothing is invented.

---

## Data honesty and limitations

- This is an **educational** dataset for practicing SQL, **not** a definitive comic
  encyclopedia.
- No long copyrighted text (descriptions, biographies, plot summaries) is stored.
- Data is only as complete and correct as the open sources. Expect some gaps and
  the occasional oddity — that is realistic and makes for good `NULL`-handling and
  data-quality discussions.
- Source metadata is recorded in the `sources` table and in the `source_url` /
  `wikidata_qid` columns so results can be traced back.

---

## Rebuilding from scratch

Just run the script again — it always recreates the database:

```bash
python build_db.py
```

To force the offline dataset (for example, with no internet), you can uninstall or
hide `requests`, or simply run the script while offline; it will detect the failure
and load `seed_manual_fallback.sql` automatically.
