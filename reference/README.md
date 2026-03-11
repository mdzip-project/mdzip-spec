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

## Why `index.md` as the required entry point name?

The name mirrors the long-established web convention of `index.html` as the default document for a directory. It is immediately familiar to anyone who has worked with static sites or web servers, and it requires no explanation to most developers.

Requiring a fixed fallback name — rather than making the entry point entirely manifest-driven — also ensures that a minimal valid `.mdz` file is as simple as possible: rename a ZIP containing `index.md` and you have a conforming archive, no manifest needed.

---

## Why JSON for the manifest?

JSON is the lowest-friction structured data format with universal library support. Every language that might implement an MDZ consumer already has a JSON parser.

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

Requiring LF absolutely would technically invalidate archives created on Windows by tools that write CRLF natively. The intent is to push the ecosystem toward a consistent default (LF is the de facto standard for source-controlled text files) without breaking existing tooling that doesn't normalize line endings.

Consumers are required (`MUST`) to accept both, so the practical interoperability impact of CRLF in an archive is zero — it just creates mild inconsistency in the raw archive contents.

---

## Why `index.md` is always required even when `entryPoint` overrides it

An earlier draft allowed `index.md` to be omitted when a manifest `entryPoint` specified a different primary document. This was reverted for backwards compatibility: a consumer that does not support `manifest.json` — whether because it predates the manifest feature or is a minimal implementation — will always look for `index.md`. Omitting it causes a silent failure with no recoverable path for those consumers.

Requiring `index.md` as a permanent fallback entry point means the format degrades gracefully. When `entryPoint` differs, producers are encouraged to make `index.md` a lightweight stub with a link to the real document, so even consumers that cannot read the manifest present the user with something actionable.

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

When a Markdown file inside an archive references an image with a relative path — e.g., `![Diagram](assets/images/diagram.svg)` — a conforming consumer resolves that path within the archive's virtual filesystem, finds the entry, and serves it inline during rendering. The image displays correctly.

If instead the `.md` file is extracted alone and opened in a generic Markdown editor, the editor looks for `assets/images/diagram.svg` on the local filesystem relative to the file's location on disk. That path doesn't exist, and the image is broken.

Extracting the entire archive first preserves the directory structure, so a generic editor may then resolve the relative paths correctly — but this defeats the portability purpose of the format and requires the user to manage extracted files manually.

This is the core reason the spec defines path resolution semantics (Section 9.3) and why tooling that understands the archive context is necessary to deliver the full `.mdz` experience. The format is inspectable without a dedicated consumer; it is only fully renderable with one.
