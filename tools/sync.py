#!/usr/bin/env python3
"""sync.py -- pull knowledge docs from local source repos into docs/ with frontmatter.

Stdlib only. Driven by sources.json at the repo root. Re-runnable and idempotent:
a second run with unchanged sources writes nothing.

    python tools/sync.py            # sync
    python tools/sync.py --check    # dry run; exit 1 if anything would change
    python tools/sync.py --check --diff
    python tools/sync.py --verbose  # also list unresolved links and duplicate checks

Source repos are read-only from here: the only git commands used are rev-parse, status
and log. Nothing is ever checked out, fetched or written in a source repo.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parent.parent
SYNC_VERSION = 1
CONFIDENCE_TAGS = ("verified", "community", "unverified", "upstream", "author")
GLOB_CHARS = set("*?[")

# Frontmatter keys, in the order they are written. Optional keys follow when present.
FM_ORDER = (
    "id", "title", "slug", "section", "game", "kind", "project", "mod", "tags",
    "source_repo", "source_path", "source_branch", "source_commit", "source_dirty",
    "generated", "generator", "superseded", "superseded_by", "phase",
    "confidence", "lines", "content_sha256", "synced_at", "sync_version",
)
FM_OPTIONAL = ("unique_title", "skill_name", "agent_name", "description",
               "agent_meta", "source_frontmatter")

RE_GENERATED_COMMENT = re.compile(r"^<!--\s*GENERATED\b", re.I)
RE_GENERATED_QUOTE = re.compile(r"^>\s*(\*\*)?(auto-)?generated(\*\*)?\s+by\b", re.I)
RE_GENERATOR = re.compile(r"\bby\s+`?([^`\s]+)`?", re.I)
RE_SUPERSEDED = re.compile(r"^>\s*(⚠️\s*)?\*\*(Replaced by|Superseded)\b")
RE_PHASE = re.compile(r"\*\*Phase (\d+), document (\d+)\.\*\*")
RE_H1 = re.compile(r"^#\s+(.+?)\s*$")
RE_CONF = re.compile(r"\[(" + "|".join(CONFIDENCE_TAGS) + r")\b")
RE_FENCE = re.compile(r"^\s{0,3}(```|~~~)")
RE_INLINE_LINK = re.compile(r"(!?\[[^\]]*\]\()(<?)([^)\s>]+)(>?)((?:\s+\"[^\"]*\")?\))")
RE_REF_DEF = re.compile(r"^(\s{0,3}\[[^\]]+\]:\s*)(\S+)(.*)$")
RE_CODE_SPAN = re.compile(r"(`+)(.+?)\1")
RE_SCHEME = re.compile(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|//|#)")
RE_FM_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$")


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def die(msg: str) -> None:
    log(f"ERROR: {msg}")
    sys.exit(2)


# --------------------------------------------------------------------------- git

def git(root: Path, *args: str) -> str:
    r = subprocess.run(
        ["git", "-c", "core.quotepath=off", *args],
        cwd=str(root), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.stdout.strip() if r.returncode == 0 else ""


class Repo:
    def __init__(self, name: str, cfg: dict):
        self.name = name
        self.root = Path(cfg["root"])
        self.game = cfg.get("game", "both")
        self.project = cfg.get("project")
        if not self.root.is_dir():
            die(f"source {name!r}: root does not exist: {self.root}")
        if git(self.root, "rev-parse", "--is-inside-work-tree") != "true":
            die(f"source {name!r}: not a git work tree: {self.root}")
        self.branch = git(self.root, "rev-parse", "--abbrev-ref", "HEAD")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.dirty_paths: set[str] = set()
        for line in git(self.root, "status", "--porcelain").splitlines():
            if len(line) > 3:
                p = line[3:].strip().strip('"')
                if " -> " in p:
                    p = p.split(" -> ", 1)[1]
                self.dirty_paths.add(p)
        self._log_cache: dict[str, str] = {}

    def last_commit(self, relpath: str) -> str:
        if relpath not in self._log_cache:
            self._log_cache[relpath] = git(self.root, "log", "-1", "--format=%H", "--", relpath)
        return self._log_cache[relpath]

    def is_dirty(self, relpath: str) -> bool:
        if relpath in self.dirty_paths:
            return True
        return any(d.endswith("/") and relpath.startswith(d) for d in self.dirty_paths)


# ---------------------------------------------------------------------- manifest

def load_manifest(path: Path) -> dict:
    try:
        m = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        die(f"cannot read manifest {path}: {e}")
    for key in ("sources", "mappings"):
        if key not in m:
            die(f"manifest is missing {key!r}")
    m.setdefault("output_dir", "docs")
    m.setdefault("global_exclude", [])
    m.setdefault("duplicates", [])
    m["mappings"] = [mp for mp in m["mappings"] if "source" in mp]  # drop $comment-only entries
    return m


def static_prefix(pattern: str) -> str:
    keep = []
    for p in pattern.split("/"):
        if GLOB_CHARS & set(p):
            break
        keep.append(p)
    return "/".join(keep)


def is_glob(pattern: str) -> bool:
    return bool(GLOB_CHARS & set(pattern))


def fnmatch_any(relpath: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if relpath == pat or fnmatch(relpath, pat):
            return True
        if pat.startswith("**/") and fnmatch(relpath, pat[3:]):
            return True
    return False


# --------------------------------------------------------------------------- docs

class Doc:
    def __init__(self, repo: Repo, relpath: str, dest: str, mapping: dict, is_txt: bool):
        self.repo = repo
        self.relpath = relpath                  # posix, relative to repo root
        self.dest = dest                        # posix, relative to output_dir, ends with .md
        self.mapping = mapping
        self.is_txt = is_txt
        self.id = dest[:-3]
        self.section = PurePosixPath(self.id).parent.as_posix() if "/" in self.id else ""
        self.slug = PurePosixPath(self.id).name
        self.meta: dict = {}
        self.body = ""
        self.links_out: list[str] = []
        self.unresolved: list[dict] = []

    @property
    def abs_path(self) -> Path:
        return self.repo.root / self.relpath


def collect(manifest: dict, repos: dict[str, Repo], verbose: bool) -> list[Doc]:
    docs: list[Doc] = []
    by_dest: dict[str, Doc] = {}
    claimed: set[tuple[str, str]] = set()
    for i, mp in enumerate(manifest["mappings"]):
        try:
            repo = repos[mp["source"]]
        except KeyError:
            die(f"mapping #{i}: unknown source {mp.get('source')!r}")
        pattern = mp["from"]
        prefix = static_prefix(pattern)
        if is_glob(pattern):
            matches = sorted(repo.root.glob(pattern))
        else:
            single = repo.root / pattern
            matches = [single] if single.is_file() else []
            if not matches:
                log(f"WARNING: mapping #{i} ({repo.name}:{pattern}) matched no file")
        base = repo.root / prefix if prefix else repo.root
        for m in matches:
            if not m.is_file():
                continue
            rel = m.relative_to(repo.root).as_posix()
            is_txt = m.suffix.lower() == ".txt"
            if m.suffix.lower() != ".md" and not (is_txt and mp.get("include_txt")):
                continue
            if fnmatch_any(rel, manifest["global_exclude"]) or fnmatch_any(rel, mp.get("exclude", [])):
                continue
            key = (repo.name, rel)
            if key in claimed:
                if verbose:
                    log(f"note: {repo.name}:{rel} already claimed by an earlier mapping; skipped in mapping #{i}")
                continue
            below = m.relative_to(base) if is_glob(pattern) else Path(m.name)
            name = below.name
            if mp.get("rename"):
                name = mp["rename"].format(name=below.name, stem=below.stem, parent=m.parent.name)
            if is_txt and not name.endswith(".md"):
                name += ".md"
            parent = below.parent.as_posix()
            if "{parent}" in (mp.get("rename") or ""):
                parent = "."          # the folder name became the file name: flatten
            dest = (PurePosixPath(mp["to"]) / (parent if parent != "." else "") / name).as_posix()
            if dest in by_dest:
                other = by_dest[dest]
                die(f"destination collision: {dest} from {repo.name}:{rel} and {other.repo.name}:{other.relpath}")
            doc = Doc(repo, rel, dest, mp, is_txt)
            by_dest[dest] = doc
            claimed.add(key)
            docs.append(doc)
    docs.sort(key=lambda d: d.dest)
    return docs


# ---------------------------------------------------------------------- processing

def read_normalised(path: Path) -> list[str]:
    return path.read_bytes().decode("utf-8-sig").splitlines()


def parse_simple_frontmatter(lines: list[str]) -> tuple[dict, list[str]]:
    """Strip a leading --- block (skills/agents have one). Returns (fields, remaining lines)."""
    if not lines or lines[0].strip() != "---":
        return {}, lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fields: dict = {}
            for raw in lines[1:i]:
                mm = RE_FM_LINE.match(raw)
                if mm:
                    val = mm.group(2).strip()
                    try:
                        fields[mm.group(1)] = json.loads(val)
                    except json.JSONDecodeError:
                        fields[mm.group(1)] = val
            rest = lines[i + 1:]
            while rest and not rest[0].strip():
                rest.pop(0)
            return fields, rest
    return {}, lines


def extract_title(lines: list[str]) -> str | None:
    for line in lines:
        s = line.strip()
        if not s or s.startswith("<!--"):
            continue
        mm = RE_H1.match(line)
        if mm:
            return re.sub(r"\s+", " ", mm.group(1).replace("`", "")).strip()
        return None
    return None


def detect_generated(lines: list[str]) -> tuple[bool, str | None]:
    head = lines[:6]
    for idx, line in enumerate(head):
        if (idx == 0 and RE_GENERATED_COMMENT.match(line)) or RE_GENERATED_QUOTE.match(line):
            text = line + (" " + head[idx + 1] if idx + 1 < len(head) else "")
            g = RE_GENERATOR.search(text)
            return True, (g.group(1).rstrip(".,;:") if g else None)
    return False, None


def detect_superseded(lines: list[str]) -> bool:
    return any(RE_SUPERSEDED.match(line) for line in lines[:15])


def detect_phase(lines: list[str]) -> str | None:
    for line in lines[:8]:
        mm = RE_PHASE.search(line)
        if mm:
            return f"Phase {mm.group(1)}, document {mm.group(2)}"
    return None


def count_confidence(body: str) -> dict:
    counts = {t: 0 for t in CONFIDENCE_TAGS}
    for mm in RE_CONF.finditer(body):
        counts[mm.group(1)] += 1
    return counts


class LinkResolver:
    def __init__(self, docs: list[Doc]):
        self.by_src: dict[tuple[str, str], Doc] = {(d.repo.name, d.relpath): d for d in docs}
        self.by_rel: dict[str, list[Doc]] = {}
        for d in docs:
            self.by_rel.setdefault(d.relpath, []).append(d)

    def resolve(self, doc: Doc, target: str) -> tuple[Doc | None, str]:
        """Return (target doc, reason). reason is empty on success."""
        src_dir = PurePosixPath(doc.relpath).parent.as_posix()
        joined = os.path.normpath(os.path.join(src_dir if src_dir != "." else "", target)).replace("\\", "/")
        if joined.startswith("../") or joined == "..":
            return None, "missing"
        hit = self.by_src.get((doc.repo.name, joined))
        if hit:
            return hit, ""
        cands = self.by_rel.get(joined, [])
        if cands:
            same_game = [c for c in cands if c.repo.game == doc.repo.game]
            return (same_game or cands)[0], ""
        on_disk = doc.repo.root / joined
        if target.endswith("/") or on_disk.is_dir():
            # a link to a folder resolves to that folder's README when it was synced
            readme = self.by_src.get((doc.repo.name, joined + "/README.md"))
            if readme:
                return readme, ""
            cands = self.by_rel.get(joined + "/README.md", [])     # same folder synced from another repo
            if cands:
                same_game = [c for c in cands if c.repo.game == doc.repo.game]
                return (same_game or cands)[0], ""
            return None, "directory"
        if on_disk.exists():
            return None, "excluded"
        return None, "missing"


def rewrite_links(doc: Doc, lines: list[str], resolver: LinkResolver) -> list[str]:
    out: list[str] = []
    in_fence: str | None = None
    dest_dir = PurePosixPath(doc.dest).parent.as_posix()

    def fix_target(raw: str) -> str:
        if RE_SCHEME.match(raw):
            return raw
        target, frag = raw, ""
        if "#" in target:
            target, frag = target.split("#", 1)
            frag = "#" + frag
        if not target:
            return raw
        hit, reason = resolver.resolve(doc, target)
        if hit is None:
            doc.unresolved.append({"target": raw, "reason": reason})
            return raw
        rel = os.path.relpath(hit.dest, dest_dir if dest_dir != "." else ".").replace("\\", "/")
        if hit.id not in doc.links_out:
            doc.links_out.append(hit.id)
        return rel + frag

    def fix_line(line: str) -> str:
        # inline code spans are left alone, but link text may itself contain a code span,
        # so decide per match by the position of the "](" rather than by splitting the line
        spans = [(cm.start(), cm.end()) for cm in RE_CODE_SPAN.finditer(line)]

        def repl(m: re.Match) -> str:
            paren = m.start(1) + len(m.group(1)) - 1
            if any(a <= paren < b for a, b in spans):
                return m.group(0)
            return m.group(1) + m.group(2) + fix_target(m.group(3)) + m.group(4) + m.group(5)

        return RE_INLINE_LINK.sub(repl, line)

    for line in lines:
        fm = RE_FENCE.match(line)
        if fm:
            marker = fm.group(1)
            if in_fence is None:
                in_fence = marker
            elif marker == in_fence:
                in_fence = None
            out.append(line)
            continue
        if in_fence is not None:
            out.append(line)
            continue
        rd = RE_REF_DEF.match(line)
        if rd:
            out.append(rd.group(1) + fix_target(rd.group(2)) + rd.group(3))
            continue
        out.append(fix_line(line))
    return out


def process(doc: Doc, resolver: LinkResolver) -> None:
    repo, mp = doc.repo, doc.mapping
    lines = read_normalised(doc.abs_path)
    src_fm: dict = {}
    if doc.is_txt:
        name = PurePosixPath(doc.relpath).name
        lines = [f"# {name}", "", "```text", *lines, "```"]
        title: str | None = name
        generated, generator, superseded, phase = False, None, False, None
    else:
        src_fm, lines = parse_simple_frontmatter(lines)
        title = extract_title(lines)
        generated, generator = detect_generated(lines)
        superseded = detect_superseded(lines)
        phase = detect_phase(lines)
        lines = rewrite_links(doc, lines, resolver)

    override = (mp.get("overrides") or {}).get(doc.relpath, {})
    mapping_title = mp.get("title") if not is_glob(mp["from"]) else None   # glob mappings keep each H1
    title = override.get("title") or mapping_title or title or doc.slug

    body = "\n".join(lines).rstrip("\n") + "\n"
    tags = list(mp.get("tags", [])) + list(override.get("tags", []))
    src_tag = f"source:{repo.name}"
    if src_tag not in tags:
        tags.append(src_tag)

    def pick(key, default):
        if key in override:
            return override[key]
        if key in mp:
            return mp[key]
        return default

    meta = {
        "id": doc.id,
        "title": title,
        "slug": doc.slug,
        "section": doc.section,
        "game": pick("game", repo.game),
        "kind": pick("kind", "reference"),
        "project": pick("project", repo.project),
        "mod": pick("mod", None),
        "tags": tags,
        "source_repo": repo.name,
        "source_path": doc.relpath,
        "source_branch": repo.branch,
        "source_commit": repo.last_commit(doc.relpath) or None,
        "source_dirty": repo.is_dirty(doc.relpath),
        "generated": bool(pick("generated", generated)),
        "generator": pick("generator", generator),
        "superseded": bool(pick("superseded", superseded)),
        "superseded_by": pick("superseded_by", None),
        "phase": phase,
        "confidence": count_confidence(body),
        "lines": body.count("\n"),
        "content_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "synced_at": None,  # filled in at render time
        "sync_version": SYNC_VERSION,
    }
    if src_fm:
        is_skill = "/skills/" in doc.relpath
        if "name" in src_fm:
            meta["skill_name" if is_skill else "agent_name"] = src_fm.pop("name")
        if "description" in src_fm:
            meta["description"] = src_fm.pop("description")
        agent_meta = {k: src_fm.pop(k) for k in ("tools", "model") if k in src_fm}
        if agent_meta:
            meta["agent_meta"] = agent_meta
        if src_fm:
            meta["source_frontmatter"] = src_fm
    doc.meta = meta
    doc.body = body


def resolve_title_collisions(docs: list[Doc]) -> list[tuple[str, list[str]]]:
    groups: dict[str, list[Doc]] = {}
    for d in docs:
        groups.setdefault(d.meta["title"], []).append(d)
    collisions = []
    for title, ds in groups.items():
        if len(ds) > 1:
            for d in ds:
                d.meta["unique_title"] = f"{title} ({d.section})" if d.section else title
            collisions.append((title, [d.id for d in ds]))
    return sorted(collisions)


# ------------------------------------------------------------------------ render

def dump(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=isinstance(value, dict))


def render(doc: Doc, synced_at: str) -> str:
    meta = dict(doc.meta)
    meta["synced_at"] = synced_at
    lines = ["---"]
    for k in FM_ORDER:
        lines.append(f"{k}: {dump(meta[k])}")
    for k in FM_OPTIONAL:
        if k in meta:
            lines.append(f"{k}: {dump(meta[k])}")
    lines += ["---", ""]
    return "\n".join(lines) + "\n" + doc.body


def read_existing_frontmatter(path: Path) -> dict:
    if not path.is_file():
        return {}
    fields: dict = {}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            if f.readline().rstrip("\r\n") != "---":
                return {}
            for line in f:
                line = line.rstrip("\r\n")
                if line == "---":
                    break
                mm = RE_FM_LINE.match(line)
                if mm:
                    try:
                        fields[mm.group(1)] = json.loads(mm.group(2))
                    except json.JSONDecodeError:
                        fields[mm.group(1)] = mm.group(2)
    except OSError:
        return {}
    return fields


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def build_index(docs: list[Doc], collisions, dup_results) -> str:
    out = ["# Knowledge-base index", "",
           "Generated by `tools/sync.py` from `sources.json`. Do not hand-edit; re-run the sync.", "",
           f"{len(docs)} documents. Flags: **G** generated, **S** superseded, "
           "**D** source file has uncommitted edits.", ""]
    sections: dict[str, list[Doc]] = {}
    for d in docs:
        sections.setdefault(d.section, []).append(d)
    for section in sorted(sections):
        out += [f"## {section or '(root)'}", "",
                "| Doc | Title | Kind | Game | Source | Lines | Flags |",
                "|---|---|---|---|---|---:|---|"]
        for d in sections[section]:
            m = d.meta
            flags = "".join(f for f, on in (("G", m["generated"]), ("S", m["superseded"]), ("D", m["source_dirty"])) if on)
            title = m["title"].replace("|", "\\|")
            out.append(f"| [{d.slug}]({d.dest}) | {title} | {m['kind']} | {m['game']} | {m['source_repo']} | {m['lines']} | {flags} |")
        out.append("")
    unresolved = [(d, u) for d in docs for u in d.unresolved]
    out += ["## Unresolved links", ""]
    if unresolved:
        out += ["Relative links whose target is not part of the knowledge base. They are left as written in the source.", "",
                "| Doc | Target | Reason |", "|---|---|---|"]
        for d, u in unresolved:
            out.append(f"| `{d.id}` | `{u['target']}` | {u['reason']} |")
    else:
        out.append("None.")
    out.append("")
    if collisions:
        out += ["## Title collisions", "",
                "These docs share an H1; their `unique_title` is suffixed with the section.", ""]
        for title, ids in collisions:
            out.append(f"- **{title}**: " + ", ".join(f"`{i}`" for i in ids))
        out.append("")
    if dup_results:
        out += ["## Duplicate-copy checks", "",
                "Copies of a canonical doc that live in other source repos and are deliberately not synced.", "",
                "| Canonical | Copy | Identical | Expected divergent |", "|---|---|---|---|"]
        for r in dup_results:
            out.append(f"| `{r['canonical']}` | `{r['copy']}` | {'yes' if r['identical'] else 'no'} | {'yes' if r['expect_divergent'] else 'no'} |")
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


# --------------------------------------------------------------------- duplicates

def sha_of(path: Path) -> str | None:
    if not path.is_file():
        return None
    body = "\n".join(read_normalised(path)) + "\n"
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def check_duplicates(manifest: dict, repos: dict[str, Repo]) -> list[dict]:
    results = []

    def split(ref: str) -> tuple[Repo, str]:
        name, _, rel = ref.partition(":")
        if name not in repos:
            die(f"duplicates: unknown source {name!r} in {ref!r}")
        return repos[name], rel

    for entry in manifest["duplicates"]:
        c_repo, c_pat = split(entry["canonical"])
        expect = bool(entry.get("expect_divergent"))
        if is_glob(c_pat):
            c_prefix = static_prefix(c_pat)
            files = [p for p in sorted(c_repo.root.glob(c_pat)) if p.is_file() and p.suffix == ".md"]
        else:
            c_prefix = c_pat
            files = [c_repo.root / c_pat]
        for copy_ref in entry["copies"]:
            k_repo, k_pat = split(copy_ref)
            k_prefix = static_prefix(k_pat) if is_glob(k_pat) else k_pat
            for f in files:
                rel = f.relative_to(c_repo.root).as_posix()
                copy_rel = k_prefix + rel[len(c_prefix):]
                a, b = sha_of(f), sha_of(k_repo.root / copy_rel)
                results.append({"canonical": f"{c_repo.name}:{rel}", "copy": f"{k_repo.name}:{copy_rel}",
                                "identical": a is not None and a == b, "expect_divergent": expect,
                                "copy_exists": b is not None})
    return results


# ----------------------------------------------------------------------------- main

def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(REPO_ROOT / "sources.json"))
    ap.add_argument("--check", action="store_true", help="dry run; exit 1 if anything would change")
    ap.add_argument("--diff", action="store_true", help="with --check, print unified diffs of modified files")
    ap.add_argument("--no-prune", action="store_true", help="do not delete orphaned files under the output dir")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    manifest = load_manifest(Path(args.manifest))
    out_dir = REPO_ROOT / manifest["output_dir"]
    repos = {name: Repo(name, cfg) for name, cfg in manifest["sources"].items()}
    for r in repos.values():
        dirty = f" ({len(r.dirty_paths)} dirty)" if r.dirty_paths else ""
        log(f"source {r.name}: {r.root.as_posix()} @ {r.branch} {r.head[:9]}{dirty}")

    docs = collect(manifest, repos, args.verbose)
    resolver = LinkResolver(docs)
    for d in docs:
        process(d, resolver)
    collisions = resolve_title_collisions(docs)
    dup_results = check_duplicates(manifest, repos)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    planned: dict[Path, str] = {}
    synced_at_by_id: dict[str, str] = {}
    added, modified, unchanged = [], [], []

    def classify(path: Path, text: str) -> None:
        planned[path] = text
        if not path.exists():
            added.append(path)
        elif path.read_bytes() != text.encode("utf-8"):
            modified.append(path)
        else:
            unchanged.append(path)

    for d in docs:
        path = out_dir / d.dest
        existing = read_existing_frontmatter(path)
        keep = existing.get("content_sha256") == d.meta["content_sha256"] and existing.get("synced_at")
        synced_at_by_id[d.id] = keep or now
        classify(path, render(d, synced_at_by_id[d.id]))

    catalog_path = out_dir / "catalog.json"
    index_path = out_dir / "INDEX.md"
    catalog = {
        "sync_version": SYNC_VERSION,
        "generated_at": now,
        "sources": {r.name: {"root": r.root.as_posix(), "branch": r.branch, "head": r.head,
                             "dirty_files": len(r.dirty_paths)} for r in repos.values()},
        "docs": [{**d.meta, "synced_at": synced_at_by_id[d.id], "path": f"{manifest['output_dir']}/{d.dest}",
                  "links_out": d.links_out, "unresolved_links": d.unresolved} for d in docs],
        "title_collisions": [{"title": t, "ids": ids} for t, ids in collisions],
        "duplicates": dup_results,
    }
    catalog_text = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    if catalog_path.is_file():
        old = catalog_path.read_text(encoding="utf-8")
        blank = lambda s: re.sub(r'"generated_at": "[^"]*"', '"generated_at": ""', s)
        if blank(old) == blank(catalog_text):
            catalog_text = old            # nothing but the timestamp changed: keep the old file
    classify(catalog_path, catalog_text)
    classify(index_path, build_index(docs, collisions, dup_results))

    orphans = []
    if out_dir.is_dir() and not args.no_prune:
        orphans = [p for p in out_dir.rglob("*") if p.is_file() and p not in planned]

    for r in dup_results:
        if not r["copy_exists"]:
            log(f"WARNING: duplicate copy not found: {r['copy']}")
        elif not r["identical"] and not r["expect_divergent"]:
            log(f"WARNING: {r['copy']} has drifted from canonical {r['canonical']} -- reconcile in the source repos; the copy is not synced")
        elif args.verbose:
            log(f"dup: {r['copy']} {'identical' if r['identical'] else 'divergent (expected)'}")
    if args.verbose:
        for d in docs:
            for u in d.unresolved:
                log(f"unresolved: {d.id} -> {u['target']} ({u['reason']})")

    rel = lambda p: p.relative_to(REPO_ROOT).as_posix()
    print(f"{len(docs)} docs: {len(added)} added, {len(modified)} modified, {len(unchanged)} unchanged, {len(orphans)} orphaned")
    for p in added:
        print(f"A {rel(p)}")
    for p in modified:
        print(f"M {rel(p)}")
    for p in orphans:
        print(f"D {rel(p)}")

    if args.check:
        if args.diff:
            for p in modified:
                old_lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
                new_lines = planned[p].splitlines(keepends=True)
                sys.stdout.writelines(difflib.unified_diff(old_lines, new_lines, fromfile=rel(p), tofile=rel(p) + " (new)"))
        return 1 if (added or modified or orphans) else 0

    for p in added + modified:
        write_text(p, planned[p])
    for p in orphans:
        p.unlink()
    if out_dir.is_dir():
        for p in sorted(out_dir.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            if p.is_dir() and not any(p.iterdir()):
                p.rmdir()
    return 0


if __name__ == "__main__":
    sys.exit(main())
