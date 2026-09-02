#!/usr/bin/env python3
"""chunk.py -- split the knowledge base into retrieval chunks.

Stdlib only, and deliberately so: the chunker is the half of the RAG pipeline that
must stay portable, so the same chunks can be pushed to a hosted store later without
dragging the local index's dependencies along. See rag/README.md for the rules this
implements.

    python rag/chunk.py docs/enderal/reference/bestiary.md   # preview one document
    python rag/chunk.py --all                                # chunk the corpus, audit it
    python rag/chunk.py --all --jsonl > chunks.jsonl         # dump chunks for another store

Inputs are docs/catalog.json (authoritative metadata for the synced corpus) plus the
hand-written curated/*.md, which are not in the catalog and carry only the minimal
frontmatter block.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHUNK_VERSION = 1

# Budgets in characters; ~4 chars/token keeps this module free of a tokenizer.
# 1800/3000 chars is roughly 450/750 tokens, bracketing the 300-600 target.
TARGET_CHARS = 1800
MAX_CHARS = 3000
MIN_CHARS = 400
BREADCRUMB_SEP = " › "

CONFIDENCE_TAGS = ("verified", "community", "unverified", "upstream", "author")
ZERO_CONFIDENCE = {tag: 0 for tag in CONFIDENCE_TAGS}

RE_FM_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")
RE_FENCE = re.compile(r"^\s{0,3}(```|~~~)")
RE_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
RE_TABLE_ROW = re.compile(r"^\s{0,3}\|")
RE_TABLE_DELIM = re.compile(r"^\s{0,3}\|[\s:|-]+\|?\s*$")


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def die(msg: str) -> None:
    log(f"ERROR: {msg}")
    sys.exit(2)


# ------------------------------------------------------------------ documents

@dataclass
class Document:
    id: str
    path: str          # repo-relative, posix
    meta: dict
    body: str

    @property
    def title(self) -> str:
        return self.meta.get("unique_title") or self.meta.get("title") or self.id


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    chunk_index: int
    heading_path: list[str]
    breadcrumb: str
    text: str
    n_tokens: int = 0

    @property
    def embed_text(self) -> str:
        """What actually gets embedded and indexed: breadcrumb first.

        The record-shaped documents are meaningless without it -- a row in the EGO
        conflict index says nothing until you know which table it came from.
        """
        return f"{self.breadcrumb}\n\n{self.text}"

    def as_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id, "doc_id": self.doc_id,
            "chunk_index": self.chunk_index, "heading_path": self.heading_path,
            "breadcrumb": self.breadcrumb, "text": self.text, "n_tokens": self.n_tokens,
        }


def split_frontmatter(text: str) -> tuple[dict, str]:
    """The five-line parser rag/README.md describes; mirrors sync.py's reader.

    Frontmatter values are JSON, which is valid YAML, so no YAML dependency is needed.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fields: dict = {}
            for raw in lines[1:i]:
                mm = RE_FM_LINE.match(raw)
                if mm:
                    try:
                        fields[mm.group(1)] = json.loads(mm.group(2))
                    except json.JSONDecodeError:
                        fields[mm.group(1)] = mm.group(2)
            return fields, "\n".join(lines[i + 1:]).lstrip("\n")
    return {}, text


def read_document(path: Path) -> tuple[dict, str]:
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
    return split_frontmatter(text)


def sha_of(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def iter_documents(repo_root: Path | None = None) -> list[Document]:
    """The synced corpus from docs/catalog.json, plus the curated docs by glob."""
    root = repo_root or REPO_ROOT
    catalog_path = root / "docs" / "catalog.json"
    if not catalog_path.is_file():
        die(f"{catalog_path} not found -- run tools/sync.py first")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    docs: list[Document] = []
    for entry in catalog.get("docs", []):
        path = root / entry["path"]
        if not path.is_file():
            log(f"WARNING: catalog lists {entry['path']} but it is missing on disk")
            continue
        fm, body = read_document(path)
        meta = {**entry, **fm}          # identical in practice; the catalog adds path/links_out
        meta["content_sha256"] = sha_of(body)
        docs.append(Document(id=entry["id"], path=entry["path"], meta=meta, body=body))

    for path in sorted((root / "curated").glob("*.md")):
        fm, body = read_document(path)
        doc_id = fm.get("id") or f"curated/{path.stem}"
        meta = {
            "id": doc_id, "title": fm.get("title") or doc_id, "slug": path.stem,
            "section": fm.get("section", "curated"), "game": fm.get("game", "both"),
            "kind": fm.get("kind", "curated"), "project": None, "mod": None,
            "tags": fm.get("tags", []), "source_repo": None, "source_path": None,
            "source_commit": None, "generated": False, "superseded": False,
            "superseded_by": None, "phase": None, "confidence": dict(ZERO_CONFIDENCE),
            "lines": body.count("\n"), "content_sha256": sha_of(body),
            "path": f"curated/{path.name}", "links_out": [],
        }
        docs.append(Document(id=doc_id, path=meta["path"], meta=meta, body=body))

    return docs


# ------------------------------------------------------------------ chunking

def estimate_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def split_sections(body: str) -> list[tuple[list[str], list[str]]]:
    """Split at ## and ###, tracking fences so a heading inside code is not a heading.

    Heading lines stay at the head of their section: the breadcrumb carries them for
    ranking, but keeping the literal line makes the chunk read like the document does.
    """
    sections: list[tuple[list[str], list[str]]] = []
    path: list[str] = []
    buf: list[str] = []
    in_fence = False
    fence = ""

    for line in body.split("\n"):
        m = RE_FENCE.match(line)
        if in_fence:
            buf.append(line)
            if m and line.strip().startswith(fence):
                in_fence, fence = False, ""
            continue
        if m:
            in_fence, fence = True, m.group(1)
            buf.append(line)
            continue

        mh = RE_HEADING.match(line)
        if mh:
            level, heading = len(mh.group(1)), mh.group(2).strip()
            if level <= 3:
                sections.append((list(path), buf))
                buf = [line]
                if level == 1:
                    path = []                       # the H1 is the breadcrumb root already
                elif level == 2:
                    path = [heading]
                else:
                    path = ([path[0]] if path else []) + [heading]
                continue
        buf.append(line)

    sections.append((list(path), buf))
    return [(p, b) for p, b in sections if "\n".join(b).strip()]


def common_prefix(a: list[str], b: list[str]) -> list[str]:
    out: list[str] = []
    for x, y in zip(a, b):
        if x != y:
            break
        out.append(x)
    return out


def merge_small(sections: list[tuple[list[str], list[str]]]) -> list[tuple[list[str], list[str]]]:
    """Fold undersized sections into the previous one when they share an H2.

    Without this, a document with a dozen one-line ### subsections produces a dozen
    near-useless chunks.
    """
    out: list[tuple[list[str], list[str]]] = []
    for path, lines in sections:
        text = "\n".join(lines)
        if out:
            prev_path, prev_lines = out[-1]
            prev_text = "\n".join(prev_lines)
            joinable = bool(prev_path) and bool(path) and prev_path[0] == path[0]
            undersized = len(prev_text) < MIN_CHARS or len(text) < MIN_CHARS
            if joinable and undersized and len(prev_text) + len(text) + 1 <= TARGET_CHARS:
                out[-1] = (common_prefix(prev_path, path), prev_lines + lines)
                continue
        out.append((path, lines))
    return out


def iter_blocks(lines: list[str]) -> list[list[str]]:
    """Group lines into blocks a split must not cut through: fences and table runs.

    Everything else breaks at blank lines, which is where prose wants to break anyway.
    """
    blocks: list[list[str]] = []
    cur: list[str] = []
    mode = ""
    fence = ""

    def flush() -> None:
        nonlocal cur
        if cur:
            blocks.append(cur)
            cur = []

    for line in lines:
        m = RE_FENCE.match(line)
        if mode == "fence":
            cur.append(line)
            if m and line.strip().startswith(fence):
                mode, fence = "", ""
                flush()
            continue
        if m:
            flush()
            mode, fence = "fence", m.group(1)
            cur.append(line)
            continue

        is_row = RE_TABLE_ROW.match(line) is not None
        if mode == "table" and not is_row:
            mode = ""
            flush()
        if is_row and mode != "table":
            flush()
            mode = "table"
        if is_row:
            cur.append(line)
            continue

        cur.append(line)
        if not line.strip():
            flush()

    flush()
    return blocks


def split_table(block: list[str]) -> list[list[str]]:
    """Oversized table -> parts split between rows, each repeating the header row."""
    header, rows = block[:2], block[2:]
    parts: list[list[str]] = []
    cur = list(header)
    for row in rows:
        if len(cur) > len(header) and len("\n".join(cur)) + len(row) + 1 > TARGET_CHARS:
            parts.append(cur)
            cur = list(header)
        cur.append(row)
    if len(cur) > len(header):
        parts.append(cur)
    return parts or [block]


def split_block(block: list[str]) -> list[list[str]]:
    """Break an oversized block only where it is safe to.

    A fenced code block is never split, so it may stay over budget -- that is the
    design note's rule, and a truncated code sample is worse than a long chunk. A
    table splits between rows; anything else (a long bullet run, a blockquote with no
    blank lines) splits on line boundaries.
    """
    if len("\n".join(block)) <= MAX_CHARS:
        return [block]
    if RE_FENCE.match(block[0]):
        return [block]
    if len(block) >= 3 and RE_TABLE_DELIM.match(block[1]):
        return split_table(block)

    parts: list[list[str]] = []
    cur: list[str] = []
    for line in block:
        if cur and len("\n".join(cur)) + len(line) + 1 > TARGET_CHARS:
            parts.append(cur)
            cur = []
        cur.append(line)
    if cur:
        parts.append(cur)
    return parts or [block]


def pack_section(lines: list[str]) -> list[str]:
    """One section -> one chunk when it fits, else greedy packing on block boundaries."""
    text = "\n".join(lines).strip("\n")
    if not text.strip():
        return []
    if len(text) <= MAX_CHARS:
        return [text]

    parts: list[str] = []
    buf: list[str] = []
    for block in iter_blocks(lines):
        for piece in split_block(block):
            piece_len = len("\n".join(piece))
            if buf and len("\n".join(buf)) + piece_len + 1 > TARGET_CHARS:
                chunk_text = "\n".join(buf).strip("\n")
                if chunk_text.strip():
                    parts.append(chunk_text)
                buf = []
            buf.extend(piece)
    tail = "\n".join(buf).strip("\n")
    if tail.strip():
        parts.append(tail)
    return parts or [text]


def chunk_document(doc: Document) -> list[Chunk]:
    title = doc.title
    chunks: list[Chunk] = []
    for path, lines in merge_small(split_sections(doc.body)):
        breadcrumb = BREADCRUMB_SEP.join([title, *path])
        for text in pack_section(lines):
            chunks.append(Chunk(
                chunk_id=f"{doc.id}#{len(chunks)}",
                doc_id=doc.id,
                chunk_index=len(chunks),
                heading_path=list(path),
                breadcrumb=breadcrumb,
                text=text,
                n_tokens=estimate_tokens(text),
            ))
    if not chunks:                      # a body with no prose; keep one chunk so it is findable
        body = doc.body.strip()
        if body:
            chunks.append(Chunk(f"{doc.id}#0", doc.id, 0, [], title, body,
                                estimate_tokens(body)))
    return chunks


# ---------------------------------------------------------------------- main

def preview(path: Path) -> None:
    fm, body = read_document(path)
    doc = Document(id=fm.get("id", path.stem), path=str(path), meta=fm, body=body)
    chunks = chunk_document(doc)
    print(f"{doc.id}: {len(chunks)} chunks from {len(body)} chars")
    for c in chunks:
        head = c.text.split("\n", 1)[0][:70]
        print(f"  [{c.chunk_index:>3}] {len(c.text):>5}c ~{c.n_tokens:>4}t  {c.breadcrumb}")
        print(f"        {head}")


def audit(docs: list[Document]) -> int:
    """Chunk everything and report the invariants the design note asks for."""
    total = oversize = fence_split = 0
    per_doc: list[tuple[int, str]] = []
    for doc in docs:
        chunks = chunk_document(doc)
        total += len(chunks)
        per_doc.append((len(chunks), doc.id))
        for c in chunks:
            if len(c.text) > MAX_CHARS:
                oversize += 1
            if c.text.count("```") % 2:
                fence_split += 1
                log(f"  fence split in {c.chunk_id}")
    per_doc.sort(reverse=True)
    print(f"{len(docs)} documents -> {total} chunks (avg {total / max(1, len(docs)):.1f}/doc)")
    print(f"oversize (> {MAX_CHARS} chars): {oversize}   unbalanced code fences: {fence_split}")
    print("largest documents:")
    for n, doc_id in per_doc[:8]:
        print(f"  {n:>4} chunks  {doc_id}")
    return 1 if fence_split else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chunk the knowledge base.")
    ap.add_argument("path", nargs="?", help="a single markdown file to preview")
    ap.add_argument("--all", action="store_true", help="chunk the whole corpus and audit it")
    ap.add_argument("--jsonl", action="store_true", help="with --all: dump chunks as JSONL")
    args = ap.parse_args(argv)

    if args.all:
        docs = iter_documents()
        if args.jsonl:
            for doc in docs:
                for c in chunk_document(doc):
                    row = c.as_dict()
                    row["meta"] = doc.meta
                    print(json.dumps(row, ensure_ascii=False))
            return 0
        return audit(docs)

    if not args.path:
        ap.error("give a markdown file, or --all")
    path = Path(args.path)
    if not path.is_file():
        die(f"{path} not found")
    preview(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
