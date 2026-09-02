#!/usr/bin/env python3
"""index.py -- build and refresh the retrieval index.

Incremental by content hash, the way tools/sync.py is incremental by file bytes: a
document is re-chunked and re-embedded only when its body changed, and a changed id is
a delete plus an add. A second --build with nothing changed does no work.

    python rag/index.py --build            # refresh (creates the index if absent)
    python rag/index.py --check            # what is stale; exit 1 if anything
    python rag/index.py --rebuild          # from scratch
    python rag/index.py --stats            # what is in the index
    python rag/index.py --eval             # retrieval quality against rag/eval.jsonl

Exit codes match sync.py: 0 ok, 1 (--check only) work pending, 2 error.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import chunk as chunker                         # noqa: E402
import embed                                    # noqa: E402
from store import DEFAULT_DB, Filters, Store    # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
EVAL_PATH = Path(__file__).resolve().parent / "eval.jsonl"
EMBED_BATCH = 256


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def die(msg: str) -> None:
    log(f"ERROR: {msg}")
    sys.exit(2)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def catalog_stamp() -> str:
    path = REPO_ROOT / "docs" / "catalog.json"
    if not path.is_file():
        return ""
    return json.loads(path.read_text(encoding="utf-8")).get("generated_at", "")


# ----------------------------------------------------------------- building

def plan(store: Store, docs: list) -> tuple[list, list, list[str]]:
    existing = store.document_hashes()
    wanted = {d.id: d for d in docs}
    added = [d for d in docs if d.id not in existing]
    changed = [d for d in docs
               if d.id in existing and existing[d.id] != d.meta["content_sha256"]]
    removed = sorted(i for i in existing if i not in wanted)
    return added, changed, removed


def pending_embeddings(store: Store) -> list[tuple[str, str]]:
    """Chunks that should have a vector but do not -- new ones, or a lexical-only build."""
    rows = store.db.execute(
        "SELECT c.chunk_id, c.breadcrumb, c.text FROM chunks c"
        " LEFT JOIN embeddings e ON e.chunk_id = c.chunk_id"
        " WHERE c.generated = 0 AND e.chunk_id IS NULL"
        " ORDER BY c.chunk_id").fetchall()
    return [(r["chunk_id"], f"{r['breadcrumb']}\n\n{r['text']}") for r in rows]


def build(check: bool = False, rebuild: bool = False, lexical_only: bool = False) -> int:
    db_path = Path(DEFAULT_DB)
    if rebuild and not check and db_path.is_file():
        db_path.unlink()
        for extra in (db_path.with_suffix(".sqlite3-wal"), db_path.with_suffix(".sqlite3-shm")):
            extra.unlink(missing_ok=True)

    docs = chunker.iter_documents(REPO_ROOT)
    if not docs:
        die("no documents found")

    fresh = not db_path.is_file()
    if fresh and check:
        print(f"index missing: {len(docs)} documents to add")
        return 1

    store = Store(db_path, create=True)
    try:
        model_changed = (store.get_meta("embed_model") not in (None, embed.MODEL_NAME))
        if model_changed and not check:
            log(f"embedding model changed -> re-embedding "
                f"({store.get_meta('embed_model')} -> {embed.MODEL_NAME})")
            store.db.execute("DELETE FROM embeddings")

        added, changed, removed = plan(store, docs)

        if check:
            for doc in added:
                print(f"A {doc.id}")
            for doc in changed:
                print(f"M {doc.id}")
            for doc_id in removed:
                print(f"D {doc_id}")
            missing = len(pending_embeddings(store)) if not lexical_only else 0
            if missing:
                print(f"E {missing} chunks awaiting embeddings")
            stale_catalog = store.get_meta("catalog_generated_at") != catalog_stamp()
            if stale_catalog and not (added or changed or removed):
                print("catalog timestamp moved but no document body changed")
            total = len(added) + len(changed) + len(removed) + missing
            print(f"{len(added)} added, {len(changed)} modified, {len(removed)} deleted,"
                  f" {missing} to embed")
            return 1 if total else 0

        for doc_id in removed:
            store.delete_document(doc_id)
        n_chunks = 0
        for doc in added + changed:
            chunks = chunker.chunk_document(doc)
            store.put_document(doc.meta, chunks)
            n_chunks += len(chunks)
        store.commit()

        embedded = 0
        if not lexical_only:
            todo = pending_embeddings(store)
            if todo and embed.available():
                started = time.monotonic()
                for i in range(0, len(todo), EMBED_BATCH):
                    batch = todo[i:i + EMBED_BATCH]
                    vecs = embed.embed_passages([t for _, t in batch])
                    store.put_embeddings(
                        [(cid, vecs[j].tobytes()) for j, (cid, _) in enumerate(batch)])
                    store.commit()
                    embedded += len(batch)
                    log(f"  embedded {embedded}/{len(todo)}")
                log(f"  embedding took {time.monotonic() - started:.1f}s")
                store.set_meta("embed_model", embed.MODEL_NAME)
                store.set_meta("embed_dim", str(embed.EMBED_DIM))
            elif todo:
                log(f"WARNING: {len(todo)} chunks left unembedded; lexical search only")

        store.set_meta("schema_version", "1")
        store.set_meta("chunk_version", str(chunker.CHUNK_VERSION))
        store.set_meta("built_at", now_iso())
        store.set_meta("catalog_generated_at", catalog_stamp())
        store.commit()

        print(f"{len(added)} added, {len(changed)} modified, {len(removed)} deleted; "
              f"{n_chunks} chunks written, {embedded} embedded")
        return 0
    finally:
        store.close()


# -------------------------------------------------------------------- stats

def show_stats() -> int:
    try:
        store = Store(DEFAULT_DB)
    except FileNotFoundError as exc:
        die(str(exc))
    with store:
        s = store.stats()
        print(f"index      {store.path}")
        print(f"documents  {s['documents']}  ({s['generated_docs']} generated,"
              f" {s['superseded_docs']} superseded)")
        print(f"chunks     {s['chunks']}  ({s['generated_chunks']} in generated docs)")
        print(f"embedded   {s['embedded']}  model {s['model']} dim {s['embed_dim']}")
        print(f"size       {s['db_bytes'] / 1e6:.1f} MB")
        print(f"built      {s['built_at']}  (catalog {s['catalog_generated_at']})")
        if s["catalog_generated_at"] != catalog_stamp():
            print("STALE: docs/catalog.json has moved since the last build")
    return 0


# --------------------------------------------------------------------- eval

def run_eval(k: int = 5) -> int:
    import search as searcher

    if not EVAL_PATH.is_file():
        die(f"{EVAL_PATH} not found")
    cases = [json.loads(line) for line in
             EVAL_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    try:
        store = Store(DEFAULT_DB)
    except FileNotFoundError as exc:
        die(str(exc))

    hits_at_k = 0
    mrr = 0.0
    with store:
        for case in cases:
            filters = Filters(**case.get("filters", {}))
            hits, _ = searcher.search(store, case["q"], k, filters)
            docs = []
            for h in hits:
                if h.doc_id not in docs:
                    docs.append(h.doc_id)
            expect = set(case["expect"])
            rank = next((i for i, d in enumerate(docs) if d in expect), None)
            if rank is None:
                print(f"  MISS  {case['q']}")
                print(f"        expected {sorted(expect)}")
                print(f"        got      {docs[:k]}")
            else:
                hits_at_k += 1
                mrr += 1 / (rank + 1)
                print(f"  ok #{rank + 1}  {case['q']}")
    n = len(cases)
    print(f"\nrecall@{k} {hits_at_k}/{n} = {hits_at_k / n:.2f}   MRR {mrr / n:.3f}")
    return 0 if hits_at_k == n else 1


# --------------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build and inspect the RAG index.")
    ap.add_argument("--build", action="store_true", help="incremental refresh")
    ap.add_argument("--check", action="store_true", help="dry run; exit 1 if work pending")
    ap.add_argument("--rebuild", action="store_true", help="drop the index and start over")
    ap.add_argument("--stats", action="store_true", help="describe the index")
    ap.add_argument("--eval", action="store_true", help="run rag/eval.jsonl")
    ap.add_argument("--lexical-only", action="store_true", help="skip embeddings")
    args = ap.parse_args(argv)

    if not any((args.build, args.check, args.rebuild, args.stats, args.eval)):
        ap.error("nothing to do: pass --build, --check, --rebuild, --stats or --eval")

    rc = 0
    if args.build or args.check or args.rebuild:
        rc = build(check=args.check, rebuild=args.rebuild, lexical_only=args.lexical_only)
    if args.stats and rc == 0:
        rc = show_stats()
    if args.eval and rc == 0:
        rc = run_eval()
    return rc


if __name__ == "__main__":
    sys.exit(main())
