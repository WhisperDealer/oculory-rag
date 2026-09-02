#!/usr/bin/env python3
"""gamedata.py -- lookup index over the decompiled game files.

The Spriggit YAML dumps and Papyrus source in the source repos are ~357,000 unique
files of copyrighted Bethesda and SureAI content. Three consequences shape this module,
and none of them apply to the prose corpus in store.py:

1. They are indexed IN PLACE and never copied here. The index holds paths; bodies are
   read from the source repos on demand. No copyrighted byte enters this repo.
2. Nothing is embedded. At this machine's throughput one chunk per record would be
   ~55 hours of CPU, and rag/README.md already prescribes the right shape for lookup
   data: a BM25/exact-match index keyed on EditorID and FormID.
3. Identity comes from the filename -- "<EditorID> - <FormID>_<plugin>.yaml" -- so the
   whole corpus can be enumerated without opening anything. Only the English display
   name needs a bounded read of each file's head.

    python rag/gamedata.py --build      # incremental; skips unchanged files
    python rag/gamedata.py --check      # what is stale; exit 1 if anything
    python rag/gamedata.py --stats
    python rag/gamedata.py --find "Blades Sword"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path(__file__).resolve().parent / "gamesources.json"
DEFAULT_DB = Path(__file__).resolve().parent / "index" / "gamedata.sqlite3"
SCHEMA_VERSION = 1

HEAD_BYTES = 8192        # enough to reach the Name block on every record type seen
READ_WORKERS = 16        # I/O bound; the reads are what cost, not the parsing
COMMIT_EVERY = 20000

RE_RECORD_NAME = re.compile(
    r"^(?:(?P<eid>.*) - )?(?P<fid>[0-9A-Fa-f]{6,8})_(?P<plugin>.+)$")
RE_NAME_KEY = re.compile(r"^(?:Name|FULL):\s*(.*)$")
RE_STRING = re.compile(r"^\s*String:\s*(.*)$")
RE_LANGUAGE = re.compile(r"^\s*- Language:\s*(\S+)\s*$")
RE_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|[_\-]+")

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE IF NOT EXISTS records (
    id          INTEGER PRIMARY KEY,
    editor_id   TEXT,
    form_id     TEXT,
    plugin      TEXT,
    form_key    TEXT,
    record_type TEXT,
    game        TEXT,
    source_set  TEXT,
    name_en     TEXT,
    path        TEXT UNIQUE,
    size        INTEGER,
    mtime       INTEGER
);
CREATE INDEX IF NOT EXISTS records_eid  ON records(editor_id);
CREATE INDEX IF NOT EXISTS records_fkey ON records(form_key);
CREATE INDEX IF NOT EXISTS records_type ON records(record_type);

CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(
    editor_id, editor_id_split, name_en, record_type,
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TABLE IF NOT EXISTS scripts (
    id         INTEGER PRIMARY KEY,
    name       TEXT,
    game       TEXT,
    source_set TEXT,
    path       TEXT UNIQUE,
    size       INTEGER,
    mtime      INTEGER,
    text       TEXT
);
CREATE INDEX IF NOT EXISTS scripts_name ON scripts(name);

CREATE VIRTUAL TABLE IF NOT EXISTS scripts_fts USING fts5(
    name, name_split, text, tokenize='unicode61 remove_diacritics 2'
);
"""


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def die(msg: str) -> None:
    log(f"ERROR: {msg}")
    sys.exit(2)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def split_identifier(text: str) -> str:
    """AkaviriKatana -> 'Akaviri Katana', so a two-word query finds a one-word EditorID."""
    return " ".join(p for p in RE_CAMEL.split(text or "") if p)


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def extract_name(text: str) -> str:
    """The English display name from a Spriggit record head.

    Records carry nine localisations; eight of them are noise that would wreck both the
    lexical index and any future embedding. Take English, in either the inline form
    (Name: Foo) or the localised block form.
    """
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = RE_NAME_KEY.match(line)
        if not m:
            continue
        inline = m.group(1).strip()
        if inline and inline not in ("|", ">", "|-", ">-"):
            return unquote(inline)
        for j in range(i + 1, min(i + 120, len(lines))):
            nxt = lines[j]
            if nxt and not nxt[0].isspace():
                break                       # dedented out of the Name block
            lang = RE_LANGUAGE.match(nxt)
            if lang and lang.group(1) == "English":
                for k in range(j + 1, min(j + 4, len(lines))):
                    ms = RE_STRING.match(lines[k])
                    if ms:
                        return unquote(ms.group(1))
        return ""
    return ""


def trim_localisations(text: str) -> str:
    """Drop the eight non-English localisation entries from a record before showing it.

    Roughly halves the tokens a record costs to read without losing anything an
    English-language answer needs.
    """
    out: list[str] = []
    skip_indent: int | None = None
    dropped = 0
    for line in text.split("\n"):
        if skip_indent is not None:
            indent = len(line) - len(line.lstrip())
            if line.strip() and indent <= skip_indent and not RE_STRING.match(line):
                skip_indent = None
            else:
                continue
        lang = RE_LANGUAGE.match(line)
        if lang and lang.group(1) != "English":
            skip_indent = len(line) - len(line.lstrip())
            dropped += 1
            continue
        out.append(line)
    result = "\n".join(out)
    if dropped:
        result += f"\n# ({dropped} non-English localisations omitted)"
    return result


# ------------------------------------------------------------------ manifest

@dataclass
class SourceSet:
    name: str
    root: Path
    game: str
    kind: str
    plugin: str | None = None
    note: str | None = None


def load_manifest(path: Path = MANIFEST) -> tuple[list[SourceSet], list[dict]]:
    if not path.is_file():
        die(f"{path} not found")
    data = json.loads(path.read_text(encoding="utf-8"))
    sets: list[SourceSet] = []
    for entry in data.get("sets", []):
        root = Path(entry["root"])
        if not root.is_dir():
            log(f"WARNING: source set {entry['name']!r} missing on disk: {root}")
            continue
        sets.append(SourceSet(entry["name"], root, entry["game"], entry["kind"],
                              entry.get("plugin"), entry.get("note")))
    if not sets:
        die("no source sets present on disk -- check the roots in gamesources.json")
    return sets, data.get("skipped", [])


# ------------------------------------------------------------------- walking

def walk_records(sset: SourceSet):
    """Yield (path, record_type, editor_id, form_id, plugin, size, mtime) per record.

    Spriggit writes two layouts. Most record types are one file per record, named for it.
    Cells, Worldspaces and DialogTopics instead get a directory per record, named for the
    record, holding RecordData.yaml -- so for those the identity is on the parent folder.
    GroupRecordData.yaml is container metadata with no EditorID and is skipped.
    """
    root = str(sset.root)
    prefix = len(root) + 1
    for dirpath, _dirnames, filenames in os.walk(root):
        rel = dirpath[prefix:] if len(dirpath) > prefix else ""
        record_type = rel.split(os.sep)[0] if rel else ""
        for fn in filenames:
            if not fn.endswith(".yaml") or fn == "GroupRecordData.yaml":
                continue
            ident = os.path.basename(dirpath) if fn == "RecordData.yaml" else fn[:-5]
            m = RE_RECORD_NAME.match(ident)
            if not m:
                continue                    # the plugin's own header record
            full = os.path.join(dirpath, fn)
            try:
                st = os.stat(full)
            except OSError:
                continue
            yield (full, record_type, (m.group("eid") or "").strip(),
                   m.group("fid").upper(), m.group("plugin"), st.st_size, int(st.st_mtime))


def walk_scripts(sset: SourceSet):
    root = str(sset.root)
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.lower().endswith(".psc"):
                continue
            full = os.path.join(dirpath, fn)
            try:
                st = os.stat(full)
            except OSError:
                continue
            yield (full, fn[:-4], st.st_size, int(st.st_mtime))


def read_head(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return f.read(HEAD_BYTES).decode("utf-8", "replace")
    except OSError:
        return ""


def read_all(path: str) -> str:
    try:
        with open(path, "rb") as f:
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


# -------------------------------------------------------------------- store

class GameStore:
    def __init__(self, path: Path | str = DEFAULT_DB, create: bool = False) -> None:
        self.path = Path(path)
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        elif not self.path.is_file():
            raise FileNotFoundError(
                f"{self.path} not found -- build it with: python rag/gamedata.py --build")
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=OFF")
        if create:
            self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> GameStore:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def get_meta(self, key: str, default=None):
        row = self.db.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set_meta(self, key: str, value) -> None:
        self.db.execute("INSERT INTO meta(key, value) VALUES(?, ?) "
                        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                        (key, str(value)))

    def known(self, table: str, source_set: str) -> dict[str, tuple[int, int]]:
        rows = self.db.execute(
            f"SELECT path, size, mtime FROM {table} WHERE source_set = ?", (source_set,))
        return {r["path"]: (r["size"], r["mtime"]) for r in rows}

    def drop_set(self, source_set: str) -> None:
        for table in ("records", "scripts"):
            ids = [r["id"] for r in self.db.execute(
                f"SELECT id FROM {table} WHERE source_set = ?", (source_set,))]
            fts = f"{table}_fts"
            for i in range(0, len(ids), 500):
                batch = ids[i:i + 500]
                marks = ",".join("?" * len(batch))
                self.db.execute(f"DELETE FROM {fts} WHERE rowid IN ({marks})", batch)
            self.db.execute(f"DELETE FROM {table} WHERE source_set = ?", (source_set,))

    # ------------------------------------------------------------ queries

    def find(self, query: str, kind: str = "any", game: str | None = None,
             record_type: str | None = None, plugin: str | None = None,
             limit: int = 20) -> list[sqlite3.Row]:
        from store import fts_query
        out: list[sqlite3.Row] = []
        exact = self._exact(query, game, limit)
        seen = {r["path"] for r in exact}
        out.extend(exact)

        match = fts_query(query)
        if not match:
            return out[:limit]

        if kind in ("any", "record"):
            where, params = ["records_fts MATCH ?"], [match]
            if game:
                where.append("r.game IN (?, 'both')")
                params.append(game)
            if record_type:
                where.append("r.record_type = ?")
                params.append(record_type)
            if plugin:
                where.append("r.plugin = ?")
                params.append(plugin)
            sql = ("SELECT r.*, 'record' AS kind,"
                   " bm25(records_fts, 4.0, 3.0, 3.0, 1.0) AS score"
                   " FROM records_fts JOIN records r ON r.id = records_fts.rowid"
                   f" WHERE {' AND '.join(where)} ORDER BY score LIMIT ?")
            for row in self.db.execute(sql, [*params, limit]):
                if row["path"] not in seen:
                    seen.add(row["path"])
                    out.append(row)

        if kind in ("any", "script"):
            where, params = ["scripts_fts MATCH ?"], [match]
            if game:
                where.append("s.game IN (?, 'both')")
                params.append(game)
            sql = ("SELECT s.id, s.name, s.game, s.source_set, s.path, s.size,"
                   " 'script' AS kind, bm25(scripts_fts, 5.0, 4.0, 1.0) AS score"
                   " FROM scripts_fts JOIN scripts s ON s.id = scripts_fts.rowid"
                   f" WHERE {' AND '.join(where)} ORDER BY score LIMIT ?")
            for row in self.db.execute(sql, [*params, limit]):
                if row["path"] not in seen:
                    seen.add(row["path"])
                    out.append(row)

        return out[:limit]

    def _exact(self, query: str, game: str | None, limit: int) -> list[sqlite3.Row]:
        """EditorID, FormID or FormKey hits come first -- an exact name is not a guess."""
        q = query.strip()
        clauses = []
        params: list = []
        if re.fullmatch(r"[0-9A-Fa-f]{6,8}", q):
            clauses.append("UPPER(form_id) = UPPER(?)")
            params.append(q.upper())
        if ":" in q:
            clauses.append("UPPER(form_key) = UPPER(?)")
            params.append(q)
        if re.fullmatch(r"[A-Za-z0-9_]+", q):
            clauses.append("UPPER(editor_id) = UPPER(?)")
            params.append(q)
        if not clauses:
            return []
        sql = ("SELECT *, 'record' AS kind, -100.0 AS score FROM records"
               f" WHERE ({' OR '.join(clauses)})")
        if game:
            sql += " AND game IN (?, 'both')"
            params.append(game)
        sql += " LIMIT ?"
        params.append(limit)
        return list(self.db.execute(sql, params))

    def record_by_path(self, path: str) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM records WHERE path = ?", (path,)).fetchone()

    def script_by_name(self, name: str) -> sqlite3.Row | None:
        return self.db.execute(
            "SELECT * FROM scripts WHERE UPPER(name) = UPPER(?) LIMIT 1", (name,)).fetchone()

    def stats(self) -> dict:
        one = lambda sql: self.db.execute(sql).fetchone()[0]  # noqa: E731
        by_set = list(self.db.execute(
            "SELECT source_set, game, COUNT(*) n FROM records GROUP BY source_set, game"
            " UNION ALL"
            " SELECT source_set, game, COUNT(*) n FROM scripts GROUP BY source_set, game"))
        return {
            "records": one("SELECT COUNT(*) FROM records"),
            "scripts": one("SELECT COUNT(*) FROM scripts"),
            "named": one("SELECT COUNT(*) FROM records WHERE name_en <> ''"),
            "types": one("SELECT COUNT(DISTINCT record_type) FROM records"),
            "db_bytes": self.path.stat().st_size if self.path.is_file() else 0,
            "built_at": self.get_meta("built_at"),
            "by_set": by_set,
        }


# -------------------------------------------------------------------- build

def build_records(store: GameStore, sset: SourceSet, check: bool) -> tuple[int, int]:
    known = store.known("records", sset.name)
    found = list(walk_records(sset))
    todo = [f for f in found if known.get(f[0]) != (f[5], f[6])]
    gone = len(known) - (len(found) - len(todo))
    if check or not todo:
        return len(todo), max(0, gone)

    log(f"  {sset.name}: {len(todo)} of {len(found)} records to index")
    paths = [f[0] for f in todo]
    done = 0
    with ThreadPoolExecutor(max_workers=READ_WORKERS) as pool:
        for i in range(0, len(todo), COMMIT_EVERY):
            batch = todo[i:i + COMMIT_EVERY]
            heads = list(pool.map(read_head, paths[i:i + COMMIT_EVERY]))
            for (path, rtype, eid, fid, plugin, size, mtime), head in zip(batch, heads):
                name_en = extract_name(head)
                store.db.execute("DELETE FROM records_fts WHERE rowid IN"
                                 " (SELECT id FROM records WHERE path = ?)", (path,))
                store.db.execute("DELETE FROM records WHERE path = ?", (path,))
                cur = store.db.execute(
                    "INSERT INTO records (editor_id, form_id, plugin, form_key,"
                    " record_type, game, source_set, name_en, path, size, mtime)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (eid, fid, plugin, f"{fid}:{plugin}", rtype, sset.game, sset.name,
                     name_en, path, size, mtime))
                store.db.execute(
                    "INSERT INTO records_fts (rowid, editor_id, editor_id_split, name_en,"
                    " record_type) VALUES (?,?,?,?,?)",
                    (cur.lastrowid, eid, split_identifier(eid), name_en, rtype))
            store.db.commit()
            done += len(batch)
            log(f"    {done}/{len(todo)}")
    return len(todo), max(0, gone)


def build_scripts(store: GameStore, sset: SourceSet, check: bool) -> tuple[int, int]:
    known = store.known("scripts", sset.name)
    found = list(walk_scripts(sset))
    todo = [f for f in found if known.get(f[0]) != (f[2], f[3])]
    gone = len(known) - (len(found) - len(todo))
    if check or not todo:
        return len(todo), max(0, gone)

    log(f"  {sset.name}: {len(todo)} of {len(found)} scripts to index")
    with ThreadPoolExecutor(max_workers=READ_WORKERS) as pool:
        texts = list(pool.map(read_all, [f[0] for f in todo]))
    for (path, name, size, mtime), text in zip(todo, texts):
        store.db.execute("DELETE FROM scripts_fts WHERE rowid IN"
                         " (SELECT id FROM scripts WHERE path = ?)", (path,))
        store.db.execute("DELETE FROM scripts WHERE path = ?", (path,))
        cur = store.db.execute(
            "INSERT INTO scripts (name, game, source_set, path, size, mtime, text)"
            " VALUES (?,?,?,?,?,?,?)",
            (name, sset.game, sset.name, path, size, mtime, text))
        store.db.execute(
            "INSERT INTO scripts_fts (rowid, name, name_split, text) VALUES (?,?,?,?)",
            (cur.lastrowid, name, split_identifier(name), text))
    store.db.commit()
    return len(todo), max(0, gone)


def build(check: bool = False, rebuild: bool = False, only: str | None = None) -> int:
    sets, skipped = load_manifest()
    if only:
        sets = [s for s in sets if s.name == only]
        if not sets:
            die(f"no source set named {only!r}")

    db_path = Path(DEFAULT_DB)
    if rebuild and not check and db_path.is_file():
        db_path.unlink()
        for extra in (db_path.with_suffix(".sqlite3-wal"), db_path.with_suffix(".sqlite3-shm")):
            extra.unlink(missing_ok=True)
    if check and not db_path.is_file():
        print("game-data index missing; run: python rag/gamedata.py --build")
        return 1

    started = time.monotonic()
    store = GameStore(db_path, create=True)
    try:
        total_new = total_gone = 0
        for sset in sets:
            fn = build_records if sset.kind == "records" else build_scripts
            new, gone = fn(store, sset, check)
            if check and (new or gone):
                print(f"{sset.name}: {new} new/changed, {gone} removed")
            total_new += new
            total_gone += gone

        if check:
            print(f"{total_new} new or changed, {total_gone} removed")
            return 1 if (total_new or total_gone) else 0

        store.set_meta("schema_version", SCHEMA_VERSION)
        store.set_meta("built_at", now_iso())
        store.set_meta("skipped_sets", json.dumps([s["path"] for s in skipped]))
        store.db.commit()
        store.db.execute("PRAGMA optimize")
        s = store.stats()
        print(f"{s['records']} records, {s['scripts']} scripts"
              f" ({s['named']} with English names) in {time.monotonic() - started:.0f}s")
        return 0
    finally:
        store.close()


def show_stats() -> int:
    try:
        store = GameStore(DEFAULT_DB)
    except FileNotFoundError as exc:
        die(str(exc))
    with store:
        s = store.stats()
        print(f"index    {store.path}")
        print(f"records  {s['records']:,}  ({s['named']:,} with an English name,"
              f" {s['types']} record types)")
        print(f"scripts  {s['scripts']:,}")
        print(f"size     {s['db_bytes'] / 1e6:.0f} MB")
        print(f"built    {s['built_at']}")
        print("per source set:")
        for row in s["by_set"]:
            print(f"  {row['source_set']:<18} {row['game']:<8} {row['n']:>8,}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Index the decompiled game files.")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--only", help="build just one source set by name")
    ap.add_argument("--find", help="look something up")
    ap.add_argument("--game", choices=("skyrim", "enderal", "both"))
    args = ap.parse_args(argv)

    if args.find:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        with GameStore(DEFAULT_DB) as store:
            rows = store.find(args.find, game=args.game)
            if not rows:
                print("no matches")
            for r in rows:
                if r["kind"] == "script":
                    print(f"  script     {r['name'][:38]:<38} {r['game']:<8}"
                          f" {r['source_set']}")
                else:
                    print(f"  {r['record_type'][:10]:<10} {r['editor_id'][:38]:<38}"
                          f" {r['form_id']:<8} {r['game']:<8}"
                          f" {r['source_set']:<15} {r['name_en'][:26]}")
        return 0

    if not any((args.build, args.check, args.rebuild, args.stats)):
        ap.error("pass --build, --check, --rebuild, --stats or --find")
    rc = 0
    if args.build or args.check or args.rebuild:
        rc = build(check=args.check, rebuild=args.rebuild, only=args.only)
    if args.stats and rc == 0:
        rc = show_stats()
    return rc


if __name__ == "__main__":
    sys.exit(main())
