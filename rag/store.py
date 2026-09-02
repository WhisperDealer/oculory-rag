#!/usr/bin/env python3
"""store.py -- the SQLite index behind the retriever.

One file holds everything derived: document metadata, chunks, the FTS5 lexical index
and the embedding vectors. It is gitignored and rebuildable; nothing here is a source
of truth. Kept separate from chunk.py so the same chunks could be pushed to a hosted
store instead, per rag/README.md.

Lexical retrieval needs no dependency at all -- CPython ships SQLite with FTS5 and
bm25() compiled in. numpy is imported lazily so a machine without the embedding stack
can still run the lexical half.
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_DB = Path(__file__).resolve().parent / "index" / "oculory.sqlite3"

# Headings carry more signal than body prose, so the breadcrumb column is weighted up.
BM25_WEIGHTS = (2.0, 1.0)

RE_FTS_TERM = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-']*")

# Terms are OR-ed, so a stopword does not just score ~0 -- it drags in every chunk that
# happens to contain it and dilutes the candidate pool the fusion sees. Questions phrased
# as questions ("what does X do about Y") are mostly stopwords, so this matters here.
STOPWORDS = frozenset("""
a about all an and any are as at be been but by can could did do does doing done for
from get give giving had has have how i if in into is it its just like make me my no not
of off on one only or other our out over should so som some such than that the their
them then there these they this those to up use used using very was way we were what
when where which while who why will with would you your
""".split())

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS documents (
    id              TEXT PRIMARY KEY,
    title           TEXT,
    slug            TEXT,
    section         TEXT,
    game            TEXT,
    kind            TEXT,
    project         TEXT,
    mod             TEXT,
    tags            TEXT,      -- JSON list
    source_repo     TEXT,
    source_path     TEXT,
    source_commit   TEXT,
    generated       INTEGER,
    superseded      INTEGER,
    superseded_by   TEXT,
    phase           TEXT,
    confidence      TEXT,      -- JSON object, the five counts
    verified        INTEGER,   -- confidence.verified, lifted out for ranking
    lines           INTEGER,
    content_sha256  TEXT,
    path            TEXT,
    links_out       TEXT,      -- JSON list of doc ids
    n_chunks        INTEGER
);

CREATE TABLE IF NOT EXISTS chunks (
    id           INTEGER PRIMARY KEY,   -- rowid, mirrored into chunks_fts
    chunk_id     TEXT UNIQUE NOT NULL,
    doc_id       TEXT NOT NULL,
    chunk_index  INTEGER,
    heading_path TEXT,                  -- JSON list
    breadcrumb   TEXT,
    text         TEXT,
    n_tokens     INTEGER,
    game         TEXT,                  -- denormalised so filtering precedes scoring
    generated    INTEGER,
    superseded   INTEGER
);

CREATE INDEX IF NOT EXISTS chunks_doc ON chunks(doc_id);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    breadcrumb, text, tokenize='unicode61 remove_diacritics 2'
);

CREATE TABLE IF NOT EXISTS embeddings (
    chunk_id TEXT PRIMARY KEY,
    vec      BLOB
);
"""


@dataclass
class Filters:
    """Metadata filters. game is the first filter and 'both' is always eligible."""
    game: str | None = None
    section: str | None = None
    kind: str | None = None
    project: str | None = None
    mod: str | None = None
    tag: str | None = None
    doc_id: str | None = None
    include_generated: bool = False
    include_superseded: bool = False
    only_generated: bool = False

    def where(self) -> tuple[str, list]:
        clauses: list[str] = []
        params: list = []
        if self.game:
            clauses.append("c.game IN (?, 'both')")
            params.append(self.game)
        if self.section:
            clauses.append("(d.section = ? OR d.section LIKE ?)")
            params += [self.section, f"{self.section}/%"]
        if self.kind:
            clauses.append("d.kind = ?")
            params.append(self.kind)
        if self.project:
            clauses.append("d.project = ?")
            params.append(self.project)
        if self.mod:
            clauses.append("d.mod = ?")
            params.append(self.mod)
        if self.tag:
            clauses.append("EXISTS (SELECT 1 FROM json_each(d.tags) WHERE json_each.value = ?)")
            params.append(self.tag)
        if self.doc_id:
            clauses.append("c.doc_id = ?")
            params.append(self.doc_id)
        if self.only_generated:
            clauses.append("c.generated = 1")
        elif not self.include_generated:
            clauses.append("c.generated = 0")
        if not self.include_superseded:
            clauses.append("c.superseded = 0")
        return (" AND ".join(clauses) if clauses else "1"), params


def fts_query(text: str) -> str:
    """Turn free text into a safe FTS5 MATCH expression.

    Every term is quoted, so nothing in a user question is ever read as an FTS
    operator. A quoted term containing dots (Skyrim.esm) becomes a phrase query over
    the tokens the unicode61 tokenizer produced, which is what we want.
    """
    terms = [t for t in RE_FTS_TERM.findall(text) if len(t) > 1 or t.isdigit()]
    kept = [t for t in terms if t.lower() not in STOPWORDS]
    terms = kept or terms          # an all-stopword query is better answered than refused
    if not terms:
        return ""
    return " OR ".join('"' + t.replace('"', '""') + '"' for t in terms[:64])


class Store:
    def __init__(self, path: Path | str = DEFAULT_DB, create: bool = False) -> None:
        self.path = Path(path)
        if create:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        elif not self.path.is_file():
            raise FileNotFoundError(
                f"{self.path} not found -- build it with: python rag/index.py --build")
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=NORMAL")
        if create:
            self.db.executescript(SCHEMA)
        self._vectors: tuple[list[str], object] | None = None

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ---------------------------------------------------------------- meta

    def get_meta(self, key: str, default: str | None = None) -> str | None:
        row = self.db.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set_meta(self, key: str, value: str) -> None:
        self.db.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, str(value)))

    # ----------------------------------------------------------- documents

    def document_hashes(self) -> dict[str, str]:
        return {r["id"]: r["content_sha256"]
                for r in self.db.execute("SELECT id, content_sha256 FROM documents")}

    def delete_document(self, doc_id: str) -> None:
        rows = self.db.execute("SELECT id, chunk_id FROM chunks WHERE doc_id = ?", (doc_id,))
        ids = [(r["id"], r["chunk_id"]) for r in rows]
        for rowid, chunk_id in ids:
            self.db.execute("DELETE FROM chunks_fts WHERE rowid = ?", (rowid,))
            self.db.execute("DELETE FROM embeddings WHERE chunk_id = ?", (chunk_id,))
        self.db.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        self.db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

    def put_document(self, meta: dict, chunks: list) -> None:
        """Replace a document and all of its chunks. A changed id is a delete plus an add."""
        self.delete_document(meta["id"])
        confidence = meta.get("confidence") or {}
        self.db.execute(
            "INSERT INTO documents (id, title, slug, section, game, kind, project, mod, tags,"
            " source_repo, source_path, source_commit, generated, superseded, superseded_by,"
            " phase, confidence, verified, lines, content_sha256, path, links_out, n_chunks)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                meta["id"], meta.get("unique_title") or meta.get("title"), meta.get("slug"),
                meta.get("section"), meta.get("game"), meta.get("kind"), meta.get("project"),
                meta.get("mod"), json.dumps(meta.get("tags") or [], ensure_ascii=False),
                meta.get("source_repo"), meta.get("source_path"), meta.get("source_commit"),
                int(bool(meta.get("generated"))), int(bool(meta.get("superseded"))),
                meta.get("superseded_by"), meta.get("phase"),
                json.dumps(confidence, sort_keys=True), int(confidence.get("verified") or 0),
                meta.get("lines"), meta.get("content_sha256"), meta.get("path"),
                json.dumps(meta.get("links_out") or [], ensure_ascii=False), len(chunks),
            ))
        generated = int(bool(meta.get("generated")))
        superseded = int(bool(meta.get("superseded")))
        for c in chunks:
            cur = self.db.execute(
                "INSERT INTO chunks (chunk_id, doc_id, chunk_index, heading_path, breadcrumb,"
                " text, n_tokens, game, generated, superseded) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (c.chunk_id, c.doc_id, c.chunk_index,
                 json.dumps(c.heading_path, ensure_ascii=False), c.breadcrumb, c.text,
                 c.n_tokens, meta.get("game"), generated, superseded))
            self.db.execute(
                "INSERT INTO chunks_fts (rowid, breadcrumb, text) VALUES (?, ?, ?)",
                (cur.lastrowid, c.breadcrumb, c.text))

    def put_embeddings(self, rows: list[tuple[str, bytes]]) -> None:
        self.db.executemany(
            "INSERT INTO embeddings (chunk_id, vec) VALUES (?, ?) "
            "ON CONFLICT(chunk_id) DO UPDATE SET vec = excluded.vec", rows)

    def commit(self) -> None:
        self.db.commit()

    # ------------------------------------------------------------ retrieval

    def lexical(self, query: str, filters: Filters, limit: int = 60) -> list[tuple[str, float]]:
        match = fts_query(query)
        if not match:
            return []
        where, params = filters.where()
        sql = (
            f"SELECT c.chunk_id AS chunk_id, bm25(chunks_fts, {BM25_WEIGHTS[0]},"
            f" {BM25_WEIGHTS[1]}) AS score"
            " FROM chunks_fts"
            " JOIN chunks c ON c.id = chunks_fts.rowid"
            " JOIN documents d ON d.id = c.doc_id"
            f" WHERE chunks_fts MATCH ? AND {where}"
            " ORDER BY score LIMIT ?")
        rows = self.db.execute(sql, [match, *params, limit]).fetchall()
        return [(r["chunk_id"], -r["score"]) for r in rows]      # bm25 is negative; flip it

    def candidate_ids(self, filters: Filters) -> set[str]:
        where, params = filters.where()
        sql = ("SELECT c.chunk_id FROM chunks c JOIN documents d ON d.id = c.doc_id"
               f" WHERE {where}")
        return {r["chunk_id"] for r in self.db.execute(sql, params)}

    def vectors(self):
        """All embeddings as (chunk_ids, matrix). Cached: the server is long-lived."""
        if self._vectors is None:
            import numpy as np
            rows = self.db.execute(
                "SELECT chunk_id, vec FROM embeddings ORDER BY chunk_id").fetchall()
            ids = [r["chunk_id"] for r in rows]
            if rows:
                mat = np.frombuffer(b"".join(r["vec"] for r in rows), dtype="float32")
                mat = mat.reshape(len(rows), -1)
            else:
                mat = np.zeros((0, 0), dtype="float32")
            self._vectors = (ids, mat)
        return self._vectors

    def chunk_rows(self, chunk_ids: list[str]) -> dict[str, sqlite3.Row]:
        if not chunk_ids:
            return {}
        out: dict[str, sqlite3.Row] = {}
        for i in range(0, len(chunk_ids), 500):
            batch = chunk_ids[i:i + 500]
            marks = ",".join("?" * len(batch))
            sql = (
                "SELECT c.chunk_id, c.doc_id, c.chunk_index, c.heading_path, c.breadcrumb,"
                " c.text, c.n_tokens, d.title, d.section, d.game, d.kind, d.project, d.mod,"
                " d.tags, d.source_repo, d.source_path, d.confidence, d.verified,"
                " d.generated, d.superseded, d.superseded_by, d.path, d.links_out, d.n_chunks"
                " FROM chunks c JOIN documents d ON d.id = c.doc_id"
                f" WHERE c.chunk_id IN ({marks})")
            for row in self.db.execute(sql, batch):
                out[row["chunk_id"]] = row
        return out

    def document(self, doc_id: str) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()

    def document_chunks(self, doc_id: str) -> list[sqlite3.Row]:
        return self.db.execute(
            "SELECT * FROM chunks WHERE doc_id = ? ORDER BY chunk_index", (doc_id,)).fetchall()

    def list_documents(self, filters: Filters, q: str | None = None,
                       limit: int = 200) -> list[sqlite3.Row]:
        clauses: list[str] = []
        params: list = []
        if filters.section:
            clauses.append("(section = ? OR section LIKE ?)")
            params += [filters.section, f"{filters.section}/%"]
        if filters.game:
            clauses.append("game IN (?, 'both')")
            params.append(filters.game)
        for field in ("kind", "project", "mod"):
            value = getattr(filters, field)
            if value:
                clauses.append(f"{field} = ?")
                params.append(value)
        if filters.tag:
            clauses.append("EXISTS (SELECT 1 FROM json_each(tags) WHERE json_each.value = ?)")
            params.append(filters.tag)
        if q:
            clauses.append("(id LIKE ? OR title LIKE ?)")
            params += [f"%{q}%", f"%{q}%"]
        if not filters.include_superseded:
            clauses.append("superseded = 0")
        where = " AND ".join(clauses) if clauses else "1"
        sql = (f"SELECT * FROM documents WHERE {where} ORDER BY section, id LIMIT ?")
        return self.db.execute(sql, [*params, limit]).fetchall()

    def stats(self) -> dict:
        one = lambda sql: self.db.execute(sql).fetchone()[0]  # noqa: E731
        return {
            "documents": one("SELECT COUNT(*) FROM documents"),
            "chunks": one("SELECT COUNT(*) FROM chunks"),
            "embedded": one("SELECT COUNT(*) FROM embeddings"),
            "generated_docs": one("SELECT COUNT(*) FROM documents WHERE generated = 1"),
            "generated_chunks": one("SELECT COUNT(*) FROM chunks WHERE generated = 1"),
            "superseded_docs": one("SELECT COUNT(*) FROM documents WHERE superseded = 1"),
            "db_bytes": self.path.stat().st_size if self.path.is_file() else 0,
            "model": self.get_meta("embed_model"),
            "embed_dim": self.get_meta("embed_dim"),
            "built_at": self.get_meta("built_at"),
            "catalog_generated_at": self.get_meta("catalog_generated_at"),
            "schema_version": self.get_meta("schema_version"),
        }
