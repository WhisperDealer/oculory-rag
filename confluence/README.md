# Confluence sync — design note

Not built yet. This records how `docs/` is meant to map onto Confluence so the sync tool, when it
is written, has no design decisions left to make.

## Target

- Site: `https://whisperdealer.atlassian.net` (cloud id `b6212290-632e-4f1e-a49a-31f9b58c8230`).
- As of 2026-09-02 the site has only the personal space `WhisperDealer`. Create a dedicated
  space (suggested key `MODKB`, name "Modding knowledge base") before the first sync so the page
  tree is not mixed into personal pages. Record the key in `confluence/config.json` (gitignored
  along with `state.json`).
- The Atlassian MCP available in Claude Code sessions already exposes `createConfluencePage` /
  `updateConfluencePage` / `getConfluencePage` with write scopes on this site, so a first
  implementation can be driven from a session without an API token. A standalone tool would use
  the REST v2 API with `urllib` (still stdlib) and an API token.

## Page tree

- One page per folder under `docs/`, one page per document beneath it. The folder page's body is
  the folder's `README.md` when one was synced (`enderal/reference`, `mods/ego`,
  `modlists/zenderal/magic`, …); otherwise a generated stub listing its children.
- `curated/overview.md` is the space home page body; `curated/glossary.md` and
  `curated/repos.md` are top-level pages. `docs/INDEX.md` becomes a top-level "Index" page.
- Page title = `confluence_title` if present, else `title`. Confluence requires unique titles per
  space; the sync already suffixes colliding titles with their section.
- Sync order: parents before children (walk sections in path order).

## Identity and idempotence

- The frontmatter `id` is the durable key. Store it on the page as a content property
  (`kb-id`) and as a label (`kb-id-<slug>`); on each run, look pages up by property, not title.
- `content_sha256` decides whether a page body needs re-uploading. Keep a local
  `confluence/state.json` of `id → { pageId, contentSha256, version }`. A changed `id` (document
  moved in the manifest) is a new page; the old one is archived, not deleted.
- Documents with `superseded: true` get a warning panel at the top linking to `superseded_by`.
- Documents with `generated: true` get an info panel naming the generator and saying not to edit
  in Confluence.

## Body conversion

Markdown → Confluence storage format (XHTML). Needs to handle what the corpus actually uses:
GitHub tables (heavily), fenced code with language hints, blockquotes (some containing emoji and
bold), nested lists, inline code, HTML comments (drop), relative links. Relative links between
synced docs are already rewritten to in-repo paths; the tool maps them to page links via
`catalog.json`'s `links_out` graph. Links listed under `unresolved_links` are rendered as plain
text with the path in code.

Render the frontmatter as a collapsed "Source" panel: source repo, path, branch, commit, synced
date, confidence counts.

## Size

Confluence pages become slow past a few hundred KB of storage format. Known large documents:
`mods/ego/conflict-index` (6511 lines), `modlists/zenderal/magic/magic-conflicts` (2125 lines),
`projects/enderal-mods/workspace-guide` and `modlists/zenderal/workspace-guide` (100+ KB each).
Options, in preference order: split on `##` into child pages; attach the markdown as a file and
show only the head; skip and link to GitHub. Decide per document using `lines` in the
frontmatter; a threshold around 2000 lines is a reasonable start.
