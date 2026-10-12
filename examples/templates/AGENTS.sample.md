# AGENTS.md

This archive is an **MDZip (`.mdz`)** file: a ZIP container holding Markdown documents, their assets (images and other files), and usually a `manifest.json` describing them.

This file is guidance for AI agents and tools that open the archive without native `.mdz` support. It is advisory: when `manifest.json` is present, it is authoritative.

## Preferred access

Before reading or writing this archive, check whether archive-aware tooling is available, in this order:

1. An MDZip MCP server (look among your tools before assuming there isn't one).
2. An MDZip-compatible library.
3. An MDZip-compatible viewer or editor.
4. Manual ZIP inspection, as a last resort.

Archive-aware tooling can read entries and assets in memory, without extracting the archive, and can detect when a write would overwrite changes made elsewhere.

### Without MDZip tooling

- **Reading** with ordinary ZIP tools is fine. Prefer reading individual entries (for example `manifest.json` or one Markdown file) in memory over extracting the whole archive to disk.
- **Writing:** don't modify the archive with generic ZIP tools, scripts or manual byte edits. Ask the user how to proceed first; a generic write can't detect a conflicting edit made in another tool, and can break the archive's structure.

## Finding the entry point

1. If `manifest.json` has an `entryPoint`, use it. If that file isn't in the archive (paths are case-sensitive), tell the user instead of opening a different file.
2. Otherwise, use `index.md` at the archive root.
3. Otherwise, set aside these support files at the root: `README`, `AGENTS`, `LICENSE`, `CHANGELOG` and `CONTRIBUTING` (compared ignoring ASCII case, `.md` or `.markdown`). If exactly one root-level Markdown file remains, use it. If none remain and the archive has only one root-level Markdown file, use that.
4. Otherwise, don't guess; ask the user which document to open.

## Mode

Check `mode` in `manifest.json`:

- `"document"` (or no `mode`, or no manifest): the archive is one logical document. Other Markdown files are parts of it, such as chapters or appendices.
- `"project"`: the archive is a collection of separate documents. Keep them separate and preserve the links between them; don't merge them into one document unless asked.

## Assets and links

Markdown files reference images and other assets with relative paths. Resolve them from the location of the referencing file, and keep relative paths and links intact.

## Reference

- Specification: https://github.com/mdzip-project/mdzip-spec
- Website: https://mdzip.org
