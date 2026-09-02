#!/usr/bin/env python3
"""search.py -- hybrid retrieval over the index.

BM25 and cosine are fused with reciprocal rank fusion rather than by normalising two
differently-scaled scores: RRF only needs the orderings, so it copes with a chunk that
appears in one list and not the other -- which is every generated chunk, since those
are indexed lexically but never embedded.

Ranking rules come from rag/README.md: game is the first filter and 'both' is always
eligible, superseded documents are out unless asked for, generated lookup tables stay
out of the default pool but are pulled in automatically when the question carries a
FormID, EditorID or plugin name.

    python rag/search.py "how does SPID distribute perks" --game enderal
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import embed                                    # noqa: E402
from store import Filters, Store                # noqa: E402

CANDIDATES = 60          # per retriever, before fusion

# RRF's textbook k is 60, which is calibrated for TREC-scale runs over millions of
# documents. Over 2000 chunks it flattens the ranks so far that "appears in both lists"
# outweighs "ranked first with 0.82 cosine", and a noisy keyword arm then decides the
# order. k=10 keeps the top of each list decisive. Measured on rag/eval.jsonl.
RRF_K = 10
VERIFIED_BOOST = 1.06    # tie-break toward documents with measured claims
SUPERSEDED_PENALTY = 0.6
MAX_CHUNKS_PER_DOC = 3

RE_FORMID = re.compile(r"\b(?:0x[0-9A-Fa-f]{4,8}|[0-9A-Fa-f]{8})\b")
RE_PLUGIN = re.compile(r"[\w\-' ]+\.(?:esp|esm|esl)\b", re.I)
# CamelCase with an internal lower->upper hop (DragonPriestHelmEbonyAA, SkyPatcher), or
# an underscored identifier (_NNE_Boss). Anchoring on the hop rather than on a trailing
# word boundary is what lets a name ending in capitals match.
RE_EDITORID = re.compile(r"\b[A-Za-z][A-Za-z0-9]*[a-z][A-Z][A-Za-z0-9]*\b|\b\w*_[A-Za-z]\w*\b")


@dataclass
class Hit:
    chunk_id: str
    doc_id: str
    score: float
    row: object
    why: str = ""

    def as_dict(self, include_text: bool = True) -> dict:
        r = self.row
        out = {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "title": r["title"],
            "breadcrumb": r["breadcrumb"],
            "section": r["section"],
            "game": r["game"],
            "kind": r["kind"],
            "score": round(self.score, 5),
            "matched_by": self.why,
            "source": r["source_repo"] and f"{r['source_repo']}:{r['source_path']}",
            "path": r["path"],
            "confidence": json.loads(r["confidence"] or "{}"),
            "chunk": f"{r['chunk_index'] + 1} of {r['n_chunks']}",
        }
        if r["generated"]:
            out["generated"] = True
        if r["superseded"]:
            out["superseded_by"] = r["superseded_by"]
        if include_text:
            out["text"] = r["text"]
        return out


def looks_record_shaped(query: str) -> bool:
    """Does the question name a specific record, rather than ask about behaviour?"""
    return bool(RE_FORMID.search(query) or RE_PLUGIN.search(query)
                or RE_EDITORID.search(query))


def rrf(ranked: list[tuple[str, float]], weight: float = 1.0) -> dict[str, float]:
    return {cid: weight / (RRF_K + rank + 1) for rank, (cid, _) in enumerate(ranked)}


def semantic(store: Store, query: str, filters: Filters,
             limit: int = CANDIDATES) -> list[tuple[str, float]]:
    if not embed.available():
        return []
    import numpy as np

    ids, mat = store.vectors()
    if not ids:
        return []
    allowed = store.candidate_ids(filters)
    keep = [i for i, cid in enumerate(ids) if cid in allowed]
    if not keep:
        return []
    qv = embed.embed_query(query)
    if qv is None:
        return []
    sims = mat[keep] @ qv
    order = np.argsort(-sims)[:limit]
    return [(ids[keep[int(i)]], float(sims[int(i)])) for i in order]


def search(store: Store, query: str, k: int = 6, filters: Filters | None = None,
           route_records: bool = True) -> tuple[list[Hit], dict]:
    filters = filters or Filters()
    lexical = store.lexical(query, filters, CANDIDATES)
    vector = semantic(store, query, filters, CANDIDATES)

    scores: dict[str, float] = {}
    why: dict[str, set[str]] = {}
    for cid, s in rrf(lexical).items():
        scores[cid] = scores.get(cid, 0.0) + s
        why.setdefault(cid, set()).add("keyword")
    for cid, s in rrf(vector).items():
        scores[cid] = scores.get(cid, 0.0) + s
        why.setdefault(cid, set()).add("semantic")

    notes: dict = {"routed_to_generated": False, "semantic": embed.available()}
    if route_records and not filters.include_generated and looks_record_shaped(query):
        # No penalty on this arm. The design note's worry -- record rows drowning the
        # explanatory docs -- is already handled by keeping generated docs out of the
        # default pool entirely. Once the question names a specific record, the lookup
        # table is the answer, so demoting it here only buries what was asked for.
        gen = store.lexical(query, replace(filters, only_generated=True), 20)
        if gen:
            notes["routed_to_generated"] = True
            for cid, s in rrf(gen).items():
                scores[cid] = scores.get(cid, 0.0) + s
                why.setdefault(cid, set()).add("record-table")

    if not scores:
        return [], notes

    rows = store.chunk_rows(list(scores))
    hits: list[Hit] = []
    for cid, score in scores.items():
        row = rows.get(cid)
        if row is None:
            continue
        if row["verified"]:
            score *= VERIFIED_BOOST
        if row["superseded"]:
            score *= SUPERSEDED_PENALTY
        hits.append(Hit(cid, row["doc_id"], score, row, "+".join(sorted(why[cid]))))

    hits.sort(key=lambda h: -h.score)
    out: list[Hit] = []
    per_doc: dict[str, int] = {}
    for hit in hits:
        if per_doc.get(hit.doc_id, 0) >= MAX_CHUNKS_PER_DOC:
            continue
        per_doc[hit.doc_id] = per_doc.get(hit.doc_id, 0) + 1
        out.append(hit)
        if len(out) >= k:
            break
    return out, notes


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Query the knowledge base index.")
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=6)
    ap.add_argument("--game", choices=("skyrim", "enderal", "both"))
    ap.add_argument("--section")
    ap.add_argument("--kind")
    ap.add_argument("--project")
    ap.add_argument("--mod")
    ap.add_argument("--tag")
    ap.add_argument("--include-generated", action="store_true")
    ap.add_argument("--include-superseded", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--text", action="store_true", help="print the full chunk text")
    args = ap.parse_args(argv)

    filters = Filters(
        game=args.game, section=args.section, kind=args.kind, project=args.project,
        mod=args.mod, tag=args.tag, include_generated=args.include_generated,
        include_superseded=args.include_superseded)
    with Store() as store:
        hits, notes = search(store, args.query, args.k, filters)
        if args.json:
            print(json.dumps([h.as_dict(args.text) for h in hits],
                             ensure_ascii=False, indent=2))
            return 0
        if not hits:
            print("no results")
            return 0
        for hit in hits:
            print(f"[{hit.score:.4f}] {hit.chunk_id}  ({hit.why})")
            print(f"    {hit.row['breadcrumb']}")
            if args.text:
                for line in hit.row["text"].split("\n"):
                    print(f"    | {line}")
        if notes["routed_to_generated"]:
            print("\n(query looked record-shaped; the generated lookup tables were searched too)")
        if not notes["semantic"]:
            print("\n(lexical only -- embeddings unavailable)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
