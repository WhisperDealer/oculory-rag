# tools/

## `sync.py`

Pulls the documents listed in `sources.json` from the local source repos into `docs/`, stamping
frontmatter and rewriting links. Python 3 stdlib only; uses `git` read-only (`rev-parse`,
`status`, `log`).

| Flag | Effect |
|---|---|
| `--check` | Dry run. Prints `A`/`M`/`D` lines for files that would be added, modified, deleted. Exit 1 if any, else 0. |
| `--diff` | With `--check`: print unified diffs for modified files. |
| `--no-prune` | Do not delete files under `docs/` that no mapping produced. |
| `--verbose`, `-v` | Also print unresolved links, duplicate-check results and skipped double matches. |
| `--manifest PATH` | Use another manifest (default `sources.json` at the repo root). |

Exit codes: `0` ok / nothing to do, `1` (`--check` only) changes pending, `2` manifest or
source error.

Idempotency: frontmatter keys are written in a fixed order with JSON-encoded values; `synced_at`
is carried over from the existing file when the body hash is unchanged; `catalog.json` is only
rewritten when something other than its timestamp changed; only files whose bytes differ are
written. A second run with unchanged sources reports `0 added, 0 modified`.

## `sources.json` fields

Top level:

| Field | Meaning |
|---|---|
| `output_dir` | Folder the corpus is written to (`docs`). Pruned of orphans on every sync. |
| `global_exclude` | Glob list applied to every mapping (source-relative paths). |
| `sources` | Map of source name → `{ root, game, project }`. `game` and `project` are per-document defaults. |
| `mappings` | Ordered list; first mapping to match a source file wins. Entries with only `$comment` are ignored. |
| `duplicates` | Copies of a canonical file that are deliberately not synced; each is hash-compared and reported. |

Mapping entry:

| Field | Meaning |
|---|---|
| `source` | Source name from `sources`. |
| `from` | Glob relative to the repo root. `**` recurses. A literal path matches one file. |
| `to` | Destination folder under `output_dir`. Subfolders below the glob's static prefix are preserved. |
| `rename` | Destination filename pattern with `{name}`, `{stem}`, `{parent}`. Using `{parent}` flattens the file into `to/`. |
| `kind` | `reference`, `world`, `research`, `design`, `guide`, `workspace`, `modlist`. Default `reference`. |
| `game` | `skyrim`, `enderal` or `both`. Defaults to the source's game. |
| `project` / `mod` | Own-mod repo name / third-party mod name. `project` defaults to the source's project; set `null` to clear. |
| `tags` | List. `source:<name>` is always appended. |
| `title` | Overrides the H1-derived title. Only honoured for single-file mappings. |
| `include_txt` | Also match `.txt` files; they are wrapped in a `text` fence and written as `<name>.txt.md`. |
| `generated` / `generator` / `superseded` / `superseded_by` | Force the flags the sync would otherwise detect from the file's head. |
| `exclude` | Globs (source-relative) to skip within this mapping. |
| `overrides` | Map of source-relative path → any of the fields above, applied to that one file. |
| `note` | Free text for humans; ignored. |

Duplicate entry: `{ "canonical": "<source>:<path-or-glob>", "copies": ["<source>:<path-or-glob>", …], "expect_divergent": false }`.
Globs are expanded on the canonical side and mirrored onto each copy by replacing the static
prefix. A non-identical copy is a warning unless `expect_divergent` is true.

## Adding a source repo

1. Add it to `sources` with its local root, game and (if it is one of my mods) project name.
2. Add mappings for what to take. Put specific single-file mappings before broad globs.
3. If it carries a copy of a doc another repo already provides, do not map the copy; add it to
   `duplicates` instead.
4. `python tools/sync.py --check --verbose`, review, sync, commit.
