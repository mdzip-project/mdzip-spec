# Reference Notes

Non-normative design rationale and background for the `.mdz` specification.

---

## Why ZIP?

ZIP is the most widely supported archive format across all platforms and programming languages. Every major language ecosystem has a mature ZIP library. ZIP files are human-inspectable with standard tools, making the format transparent and debuggable without special software. The format is also well-understood by security tools and antivirus software.

Alternatives considered:

- **tar.gz / tar.bz2** — Common on Unix but poor native support on Windows without third-party tools. Not randomly accessible (must decompress sequentially to read a single file).
- **Custom binary format** — Maximum control but requires custom parsers everywhere, with no ecosystem leverage.
- **SQLite** — Used by formats like EPUB3 and some note-taking apps. Queryable, but not human-inspectable and requires an SQL library.

ZIP's random-access entry model is a meaningful advantage: a consumer can read `manifest.json` without extracting the entire archive.

---

## Why `index.md` as the conventional entry point name?

The name mirrors the long-established web convention of `index.html` as the default document for a directory. It is immediately familiar to anyone who has worked with static sites or web servers, and it requires no explanation to most developers.

Using a fixed conventional name rather than making the entry point entirely manifest-drive also keeps the minimal `.mdz` case simple: rename a ZIP containing `index.md` and you have a conforming archive, no manifest needed. The spec still allows a manifest `entryPoint` to override the default when present and valid.

---
## Why JSON for the manifest?

JSON is the lowest-friction structured data format with universal library support. Every language that might implement an MDZip consumer already has a JSON parser.

Alternatives considered:

- **TOML** — Readable and well-suited to configuration, but library support is less universal than JSON, particularly in browser environments.
- **YAML** — Expressive but famously has parsing pitfalls (the Norway problem, implicit type coercion) that make it a poor fit for a machine-read metadata file in an interoperability spec.
- **Front matter in `index.md`** — Avoids a separate file but mixes metadata with content, complicates parsing, and makes metadata inaccessible without reading and parsing Markdown.

---

## Why not mandate a Markdown dialect?

Mandating a dialect would exclude existing tools that already render a specific flavour well, and would add a normative dependency on a third-party specification that evolves independently. The `.mdz` format is a container, not a renderer.

In practice, most modern Markdown tooling converges on CommonMark as a baseline. Producers who rely on dialect-specific features (e.g., GFM task lists, Obsidian wikilinks) are encouraged to document that dependency in the manifest `description` or within the document itself.

---

## Why `SHOULD` for LF line endings rather than `MUST`?

Conforming producers SHOULD normalize line endings to LF when writing `.mdz` files, even if source content originated from platforms that use other line-ending conventions.

Requiring LF absolutely would technically invalidate archives created on Windows by tools that write CRLF natively. The intent is to push the ecosystem toward a consistent default (LF is the de facto standard for source-controlled text files) without breaking existing tooling that doesn't normalize line endings.

Consumers are required (`MUST`) to accept both, so the practical interoperability impact of CRLF in an archive is zero — it just creates mild inconsistency in the raw archive contents.

---
## Why no encryption or DRM?

Encryption would require key management, which is a complex problem this spec has no business solving. Any encryption scheme added here would either be weak (a false sense of security) or require significant protocol design work well outside the scope of a document container format.

ZIP's own password protection (`ZipCrypto`) is known to be cryptographically weak and is excluded explicitly. If confidentiality is required, the appropriate approach is to encrypt the `.mdz` file itself at the transport or storage layer using a purpose-built tool.

---

## Relationship to similar formats

| Format | Container | Content | Metadata |
|--------|-----------|---------|----------|
| `.mdz` | ZIP | Markdown | JSON manifest |
| EPUB | ZIP | XHTML/HTML | OPF XML |
| DOCX | ZIP (OOXML) | XML | XML |
| ODT | ZIP | XML | XML |
| Obsidian vault | Directory | Markdown | YAML front matter |

`.mdz` occupies a simpler niche than EPUB or DOCX: it intentionally avoids defining rendering behaviour, pagination, or a complex metadata schema. The goal is a minimal portable container for Markdown documents, not a full publication format.

---

## OS-reserved character restrictions in file paths

The prohibited characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) are the union of characters that are reserved or illegal in file names on the three major platforms:

- **Windows (NTFS/FAT)** — prohibits `\ / : * ? " < > |` and control characters
- **macOS (HFS+/APFS)** — prohibits `:` (used internally as path separator) and null bytes
- **Linux (ext4 and most filesystems)** — prohibits `/` and null bytes

The spec restricts the intersection that causes cross-platform failures. Forward slash (`/`) is already handled by the path separator rules. The remaining list ensures that a conforming archive can be safely extracted on any platform without name collisions or filesystem errors.

---

## Why a dedicated consumer is required for correct asset rendering

An `.mdz` file is only fully portable when opened by a tool that understands it is operating inside an archive. This is most visible with assets such as images.

When a Markdown file inside an archive references an image with a relative path — e.g., `![Diagram](images/diagram.svg)` — a conforming consumer resolves that path within the archive's virtual filesystem, finds the entry, and serves it inline during rendering. The image displays correctly.

If instead the `.md` file is extracted alone and opened in a generic Markdown editor, the editor looks for `images/diagram.svg` on the local filesystem relative to the file's location on disk. That path doesn't exist, and the image is broken.

Extracting the entire archive first preserves the directory structure, so a generic editor may then resolve the relative paths correctly — but this defeats the portability purpose of the format and requires the user to manage extracted files manually.

This is the core reason the spec defines path resolution semantics (Section 9.3) and why tooling that understands the archive context is necessary to deliver the full `.mdz` experience. The format is inspectable without a dedicated consumer; it is only fully renderable with one.

---

## Why flat asset directories instead of an `assets/` wrapper?

Earlier drafts recommended placing all assets under a single `assets/` parent directory (e.g., `assets/images/`, `assets/styles/`). This was changed to recommend type-named directories directly at the archive root (e.g., `images/`, `styles/`, `fonts/`).

The `assets/` wrapper adds a level of nesting without adding meaning. Directory names like `images/` and `styles/` are already self-describing — grouping them under `assets/` tells you nothing you couldn't already infer from the names themselves. The extra nesting makes paths longer and the structure slightly harder to read.

The `assets/` wrapper is still permitted (producers MAY use it), and it remains a reasonable choice for producers who want a clear visual boundary between content files and supporting files. But it is no longer the recommended default.

For larger projects where assets are scoped per section, the section directory itself provides the namespace, making the wrapper even less useful.

---

## Why mode semantics, and why does project mode require a manifest?

Without modes, a consumer opening a multi-file `.mdz` archive cannot know whether those files form one logical document (a book with chapters) or a collection of independent pages (a documentation site). The only alternatives are heuristics — guessing based on file count or directory structure — or leaving the interpretation to each consumer independently. Both produce inconsistent behavior across tools.

Mode semantics resolve this by making the intent explicit. Two modes are defined:

- `document` — the archive is a single logical document. This is the default and covers the vast majority of use cases.
- `project` — the archive is a collection of independent documents.

**Why is document mode the default?** Because it matches the primary use case and requires no manifest. Existing archives without a manifest remain valid. Simple producers can continue to omit the manifest entirely.

**Why does project mode require an explicit manifest?** Because mode MUST NOT be inferred from archive contents. If a consumer could guess `project` mode from the presence of multiple Markdown files, different consumers would make different guesses and behavior would diverge. Requiring an explicit declaration ensures every consumer interprets the archive the same way. The manifest is also already the natural place for interpretation metadata — it is how `entryPoint` and other behavioral properties are declared.

**Why not infer mode from file count or structure?** Inference is fragile and ambiguous. A document split into chapters has multiple Markdown files but is still one logical document. A project with a single overview page has one Markdown file but is still a project. File count and structure do not reliably indicate intent — only an explicit declaration does.


