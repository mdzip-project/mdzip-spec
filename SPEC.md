# MDZip (.mdz) File Format Specification

**Version:** 1.2.0  
**Status:** Final  
**Date:** 2026-10-13

---

## Table of Contents

1. [Overview](#1-overview)
2. [Goals and Non-Goals](#2-goals-and-non-goals)
3. [Terminology](#3-terminology)
4. [File Format](#4-file-format)
5. [Archive Structure](#5-archive-structure)
6. [Manifest File](#6-manifest-file)
7. [Markdown Content Files](#7-markdown-content-files)
8. [Asset Files](#8-asset-files)
9. [Linking and References](#9-linking-and-references)
10. [MIME Type and File Extension](#10-mime-type-and-file-extension)
11. [Versioning](#11-versioning)
12. [Compatibility Notes](#12-compatibility-notes)
13. [Security Considerations](#13-security-considerations)
14. [Conformance](#14-conformance)
15. [Examples](#15-examples)
16. [Implementation Guidance (Non-Normative)](#16-implementation-guidance-non-normative)
17. [Future Extensions (Non-Normative)](#17-future-extensions-non-normative)

---

## 1. Overview

The **MDZip** format (`.mdz`) is a portable document format that packages one or more Markdown content files together with their associated assets—such as images, stylesheets, and other referenced resources—into a single ZIP archive.

An `.mdz` file lets authors distribute a Markdown-based document together with the resources it needs, so the references between them don't break. An archive is *self-contained* when it includes every resource required to render it; links outside the archive ([Section 9.4](#94-links-outside-the-archive-optional)) and external URLs make it depend on things it does not carry. How faithfully an archive renders also depends on the Markdown dialects and asset formats the consumer supports ([Section 12.4](#124-markdown-dialect-portability)), and including a resource such as a stylesheet does not by itself define how a consumer applies it.

This specification follows established standards patterns by using RFC 2119 normative language, Semantic Versioning, and UTF-8/JSON conventions compatible with other open document and text-based standards (such as CommonMark, EPUB, and TOML ecosystems).

---

## 2. Goals and Non-Goals

### Goals

- Provide a simple, open, and inspectable container format for Markdown documents.
- Let documents and the resources they use travel together as a single unit.
- Support multiple Markdown pages/sections within a single archive.
- Stay readable and inspectable with any tool that understands ZIP and Markdown, even one that knows nothing about MDZip (it may not know the entry point, mode or extensions, but the content is never locked away).
- Remain human-inspectable using any standard ZIP utility.

### Non-Goals

- This specification does not mandate a specific Markdown dialect or rendering engine.
- This specification does not define Digital Rights Management (DRM) or encryption.
- This specification does not define a network transport protocol.
- This specification does not define ordered navigation, pagination, or table-of-contents structure for multi-page documents. Linking between pages is left to the document author using standard Markdown relative links.

---

## 3. Terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

| Term | Definition |
|------|-----------|
| **Archive** | The `.mdz` file itself; a ZIP-format container. |
| **Entry point** | The primary Markdown file a reader or tool opens first. |
| **Manifest** | The `manifest.json` file at the root of the archive describing document metadata and entry-point overrides. Optional for archive validity; conforming producers always write one (see [Section 14.1](#141-conforming-producer)). |
| **Support file** | A root-level Markdown file that describes or accompanies the archive rather than being document content: `README`, `AGENTS`, `LICENSE`, `CHANGELOG`, or `CONTRIBUTING` (see [Section 5.5](#55-entry-point-discovery)). |
| **Asset** | Any non-Markdown file in the archive that the archive uses: referenced by a Markdown file (images, stylesheets), by the manifest (such as `cover`), or by an extension or profile the archive declares (schemas, data files, templates). Also called a *resource*. |
| **Conforming producer** | Software that writes `.mdz` files — creating new archives or modifying existing ones — according to this specification. |
| **Conforming consumer** | Software that reads and/or processes `.mdz` files according to this specification. |
| **Mode** | The declared interpretation intent of an archive's contents, specified via `manifest.mode`. Controls how consumers render and navigate content. |
| **Document mode** | A mode in which the archive represents one logical publication, opened at its entry point. The default when no mode is declared. |
| **Project mode** | A mode in which the archive represents a collection of independently addressable Markdown documents. Requires an explicit manifest declaring `"mode": "project"`. |

---

## 4. File Format

An `.mdz` file is a **ZIP archive** as defined by the [ZIP Application Note (APPNOTE.TXT)](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT) version 6.3.10 or later.

Requirements:

- The archive **MUST** be a valid ZIP file.
- The archive **MUST NOT** use ZIP64 extensions unless a ZIP field cannot represent its value without them (for example, an entry or the archive exceeds 4 GB, or the archive has more than 65,535 entries).
- Files inside the archive **MUST** use UTF-8 encoded file paths. Paths may use characters from any writing system (Unicode script), such as Latin, Cyrillic, Han or Arabic; producers **SHOULD** write them in Unicode Normalization Form C (NFC). See [Section 5.4.1](#541-path-matching).
- Producers **MUST** set the UTF-8 flag (general purpose bit 11) on every entry whose name contains non-ASCII characters. Consumers **SHOULD** decode entry names as UTF-8 even when the flag is not set, because many ZIP tools write UTF-8 names without it. When an entry's name in the central directory differs from the name in its local header, consumers **MUST** use the central directory.
- File path separators inside the archive **MUST** be forward slashes (`/`).
- Each entry **MUST** be stored without compression (method 0) or compressed with DEFLATE (method 8). Conforming consumers **MUST** support both methods, and **MAY** reject an archive that uses any other method (`ERR_ZIP_INVALID`).
- The archive **MUST NOT** use password protection or encryption.
- Every entry **MUST** be a regular file or a directory. Producers **MUST NOT** write symbolic links or other special files, such as an entry whose external file attributes give a Unix file type of symbolic link (`S_IFLNK`). See [Section 13.1](#131-archive-handling) for how consumers treat them.
- Line endings: producers **SHOULD** write LF (`\n`) in Markdown files and `manifest.json` that they create or modify, and consumers **MUST** accept both LF and CRLF (`\r\n`). See [Section 12.2](#122-line-endings).

---

## 5. Archive Structure

An `.mdz` file is a ZIP archive containing at least one Markdown file that can be resolved as the primary document using the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery). A `manifest.json` file at the archive root is OPTIONAL for an archive to be valid, so a folder zipped by hand and renamed to `.mdz` remains a valid archive; conforming producers, however, **MUST** write one (see [Section 14.1](#141-conforming-producer)). All other files are organized relative to the archive root.

### 5.1 Required Files

There are no unconditionally required files beyond the archive being a valid ZIP. However, the archive **MUST** contain at least one Markdown file that satisfies the entry point discovery rules in [Section 5.5](#55-entry-point-discovery).

### 5.2 Optional Files

| Path | Description |
|------|-------------|
| `index.md` | Conventional entry point Markdown file (see [Section 5.5](#55-entry-point-discovery)). |
| `manifest.json` | Document manifest (see [Section 6](#6-manifest-file)). Optional for archive validity; written by every conforming producer. |
| `README.md` | Optional human-facing guidance for environments without full `.mdz` tooling (see [Section 5.6](#56-human-facing-readmemd-optional)). |
| `AGENTS.md` | Optional guidance for AI agents and tools without native `.mdz` support (see [Section 5.8](#58-agent-facing-agentsmd-optional)). |

### 5.3 Recommended Layout

#### Document Mode

```
document.mdz (ZIP archive)
├── index.md               # Recommended: conventional entry point
├── manifest.json          # Metadata and entry point (always written by conforming producers)
├── README.md              # Optional: human-facing usage notes
├── AGENTS.md              # Optional: guidance for AI agents and tools
├── chapter-01.md          # Additional Markdown files (optional)
├── chapter-02.md
├── images/                # Asset directories at archive root
│   ├── cover.png
│   └── diagram.svg
└── styles/
    └── style.css
```

#### Project Mode

Project archives SHOULD organize Markdown files into subdirectories by section or topic. Asset directories live at the archive root for small projects; larger projects MAY scope assets per section when it adds clarity.

**Flat assets (small to medium projects):**

```
project.mdz (ZIP archive)
├── manifest.json          # Required: must declare "mode": "project"
├── index.md               # Entry point: overview or home page
├── README.md              # Optional: human-facing usage notes
├── AGENTS.md              # Optional: guidance for AI agents and tools
├── guide/
│   ├── intro.md
│   ├── setup.md
│   └── advanced.md
├── reference/
│   ├── api.md
│   └── cli.md
├── images/                # Shared asset directories at archive root
│   ├── logo.png
│   └── banner.png
└── styles/
    └── style.css
```

**Per-section assets (larger projects):**

```
project.mdz (ZIP archive)
├── manifest.json          # Required: must declare "mode": "project"
├── index.md               # Entry point: overview or home page
├── README.md              # Optional: human-facing usage notes
├── guide/
│   ├── intro.md
│   ├── setup.md
│   └── images/            # Section-scoped assets
│       └── setup-screenshot.png
├── reference/
│   ├── api.md
│   └── images/
│       └── architecture.svg
└── styles/                # Shared styles at archive root
    └── style.css
```

### 5.4 Path Constraints

> **Note for authors:** These constraints apply to ZIP entry names inside the archive — the internal paths used to store files. They do not apply to relative links within your Markdown content (e.g., `[next chapter](guide/chapter-02.md)` or `![diagram](images/diagram.svg)`), which follow normal Markdown and relative URL conventions. Authors using a standard tool to create `.mdz` files will never need to think about this — the tool and the operating system handle it. This section is aimed at implementors building producers or consumers in code.

The ZIP format permits entry names that are unsafe or non-portable across operating systems. MDZip imposes tighter constraints to ensure archives are safe to extract and consistent across platforms.

- All entry paths inside the archive **MUST** be relative to the archive root.
- Entry paths **MUST NOT** begin with a leading slash (`/`).
- Entry paths **MUST NOT** contain `..` segments (e.g., `../escape.md` or `docs/../index.md`). A `..` inside a name, as in `notes..md`, is not a segment and is allowed. This applies to the stored names only: links in Markdown may use `../`, including to leave the archive ([Section 9.4](#94-links-outside-the-archive-optional)).
- Entry paths **MUST NOT** contain empty segments (as in `docs//intro.md`) or `.` segments (as in `./index.md` or `docs/./intro.md`). Each entry therefore has exactly one stored form, and lookups never need to normalize path syntax.
- A file entry's path **MUST NOT** end in `/`. An entry whose name ends in `/` is a *directory entry*: directory entries are optional, carry no content, are never files for entry point discovery or link resolution, and **MUST** otherwise satisfy these rules.
- An archive **MUST NOT** contain a file whose path is also a directory of another entry, such as a file `docs` together with `docs/intro.md` or a directory entry `docs/`, compared after NFC normalization.
- Entry paths **MUST NOT** contain null bytes or ASCII control characters (U+0000–U+001F, U+007F).
- Entry paths **MUST NOT** contain characters reserved by common operating systems: `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`.
- An archive **MUST NOT** contain two entries whose paths are equal after NFC normalization ([Section 5.4.1](#541-path-matching)).
- An archive **SHOULD NOT** contain two entries whose paths differ only in case (for example `Index.md` and `index.md`), because they collide when extracted to a case-insensitive filesystem such as the defaults on Windows and macOS. For this check, "differ only in case" means equal under Unicode default case folding (`CaseFolding.txt`, statuses C and F).

Uniqueness and conflicts are checked after NFC normalization, the only normalization applied to stored paths.

These rules make entry names safe, not universally extractable. A valid name can still be unusable on some filesystems — for example Windows reserved device names such as `CON.md`, or names ending in a space or period. Consumers that read entries directly from the archive are unaffected; consumers that extract to a filesystem **SHOULD** report names the target filesystem cannot represent rather than renaming them silently ([Section 13.1](#131-archive-handling)).

See [Section 13.1](#131-archive-handling) for consumer requirements on rejecting non-conforming paths.

> **Tip for authors:** names are matched case-sensitively ([Section 5.4.1](#541-path-matching)), so a link must use the same capitalization as the file it points to. Windows and macOS ignore case by default, so a mismatch such as `Images/Logo.png` for `images/logo.png` can work on the author's computer and fail everywhere else. Lowercase names make this mistake less likely, but any capitalization is valid.

#### 5.4.1 Path Matching

Whenever a consumer looks up an archive entry by path — `manifest.entryPoint`, `manifest.cover`, `index.md` in entry point discovery, or a relative link ([Section 9.3](#93-path-resolution)) — it **MUST** compare paths as follows:

1. Normalize both the path being looked up and each entry path to Unicode Normalization Form C (NFC).
2. Compare the normalized strings exactly, code point by code point. Matching is **case-sensitive**: `Index.md` does not match `index.md`.

Normalization makes visually identical paths match regardless of how they were encoded; for example, `é` stored as one code point (U+00E9) and as `e` followed by a combining acute accent (U+0065 U+0301), as some macOS tools write it, are the same path. Case-sensitive comparison keeps matching identical in every implementation and language. Case-insensitive matching is avoided because case conversion depends on language: Turkish `I` lowercases to dotless `ı`, German `ß` uppercases to `SS`, and Greek has two lowercase forms of sigma.

The only case-insensitive comparisons in this specification are for fixed ASCII names: the Markdown extensions `.md` and `.markdown` ([Section 7.3](#73-file-extensions)) and the support file names in [Section 5.5](#55-entry-point-discovery). These **MUST** be compared ASCII case-insensitively, treating only `A`–`Z` as equal to `a`–`z`. Implementations **MUST NOT** use locale-sensitive case conversion for them; for example, lowercasing `LICENSE` with Turkish rules yields `lıcense`, which would fail to match.

When a lookup fails only because of case (the paths are equal under Unicode default case folding, as in [Section 5.4](#54-path-constraints)), a consumer **SHOULD** report the near match to the user (for example, "did you mean `index.md`?"), because this is usually an authoring mistake that went unnoticed on a case-insensitive filesystem. It **MUST NOT** silently use the near match.

### 5.5 Entry Point Discovery

Conforming consumers **MUST** determine the primary Markdown file using the following ordered algorithm:

1. If `manifest.json` is present at the archive root and declares an `entryPoint`:
   - If the value is not a valid entry point path (defined below), the archive is non-conforming; the consumer **SHOULD** report `ERR_ENTRYPOINT_INVALID`.
   - Otherwise, if it matches a file in the archive ([Section 5.4.1](#541-path-matching)), use that file.
   - Otherwise, the archive is non-conforming; the consumer **SHOULD** report `ERR_ENTRYPOINT_MISSING`.

   In both non-conforming cases, the consumer **MUST NOT** silently fall back to rules 2–4. It **MAY** offer to continue with rules 2–4 as an explicit recovery, provided it shows the user a visible warning that the declared entry point is invalid or missing.

   Rules 2–4 apply only when the manifest is absent or declares no `entryPoint`.
2. If `index.md` exists at the archive root, use it.
3. Consider the `.md` and `.markdown` files at the archive root, setting aside support files (defined below):
   - If exactly one Markdown file remains, use it.
   - If none remain and exactly one root-level Markdown file exists (that is, the archive's only root-level Markdown file is a support file), use that file.
4. Otherwise, the consumer **MUST NOT** silently select a file arbitrarily. The consumer **SHOULD** present the user with a list of available Markdown files to choose from, or report a clear error indicating that no unambiguous entry point could be determined.

**Valid entry point path.** For rule 1, an `entryPoint` value is valid when it is a non-empty string that:

- is a relative archive path satisfying [Section 5.4](#54-path-constraints) (no leading `/`; no empty, `.` or `..` segments apart from the one leading `./` allowed below; forward slashes only; no control or reserved characters);
- names a file, not a directory (it does not end in `/`);
- has a `.md` or `.markdown` extension (ASCII case-insensitive, [Section 5.4.1](#541-path-matching)).

A single leading `./` is permitted and is removed before matching. A value that is valid but does not match any entry, including one that differs from an entry only in case, is *missing* rather than invalid.

**Support files.** For rule 3, a *support file* is a root-level file whose name, compared ASCII case-insensitively ([Section 5.4.1](#541-path-matching)), is one of the following, with a `.md` or `.markdown` extension:

- `README`
- `AGENTS`
- `LICENSE`
- `CHANGELOG`
- `CONTRIBUTING`

For example, `README.md`, `readme.markdown` and `AGENTS.MD` are support files; `docs/README.md` (not at the root) and `README-draft.md` are not. The list is closed: consumers **MUST NOT** treat other files as support files, so that every consumer resolves the same entry point. Future versions of this specification may extend it.

Support files describe or accompany the archive (see [Section 5.6](#56-human-facing-readmemd-optional) and [Section 5.8](#58-agent-facing-agentsmd-optional)), so adding one to an archive that has a root-level content file does not change which file rule 3 selects. For example, an archive with no manifest and no `index.md` containing `notes.md` and `AGENTS.md` resolves to `notes.md`. (An archive whose only root-level Markdown files are support files, such as `README.md` and `AGENTS.md` together, has no unambiguous entry point under rule 3; a producer adding the second one is therefore required to add a manifest, see [Section 14.1](#141-conforming-producer).)

Conforming producers **MUST** declare the entry point in `manifest.json` (see [Section 14.1](#141-conforming-producer)), which satisfies rule 1 and makes resolution unambiguous across all consumers. Rules 2–4 exist so that archives created without a conforming producer, such as a folder zipped by hand, still resolve predictably.

### 5.6 Human-Facing `README.md` (Optional)

Producers **SHOULD** include a root-level `README.md` when practical, especially for files likely to be opened by recipients without `.mdz`-aware tooling.

Because `README.md` is inside the archive, producers distributing `.mdz` to likely unaware recipients **SHOULD** provide a primary discovery method outside the archive. Examples include:

- a download-page note describing `.mdz` and basic opening steps,
- a companion sidecar text file next to the `.mdz` file,
- a website/help link shown wherever the file is shared.

When present, `README.md` **SHOULD** briefly include:

- what the archive is (`.mdz` / MDZip),
- where primary document content begins (for example, `index.md`),
- how to open the package with standard tools (for example, unzip then open Markdown files),
- where to find format documentation (for example, a project URL).

Producers **MAY** include instructions for opening the package with a specific consumer tool. When they do, they **SHOULD** also include a generic fallback workflow (for example, unzip and open `index.md`) so the package remains understandable without that specific tool.

`README.md` is a secondary aid and does not replace out-of-archive discovery guidance for unaware recipients. It is informational only and does not affect conformance logic. It is a support file, so it does not count toward rule 3 of entry point discovery ([Section 5.5](#55-entry-point-discovery)) unless it is the archive's only root-level Markdown file.

A reusable sample is available at [`examples/templates/README.sample.md`](examples/templates/README.sample.md).

### 5.7 Mode Semantics

An `.mdz` archive has an **interpretation mode** that tells conforming consumers how to render and navigate its contents. Mode is either applied by default or explicitly declared via `manifest.mode`. Mode values are case-sensitive and MUST be lowercase.

#### 5.7.1 Mode Defaults

If `manifest.json` is absent, or if `manifest.json` is present but does not include a `mode` field, consumers MUST treat the archive as `mode: "document"`. This is a default, not an inference — the rule is deterministic and requires no examination of archive contents.

The number of Markdown files present, their names, or the directory structure of the archive MUST NOT influence mode selection.

#### 5.7.2 Document Mode

`document` mode indicates that the archive represents **one logical publication**, regardless of how many Markdown files it contains.

**Consumers MUST:**

- Resolve the entry point using the standard entry point discovery algorithm (Section 5.5)
- Open the entry point as the document's initial content

Links from the entry point to other Markdown files in the archive are ordinary links ([Section 9](#9-linking-and-references)). They do not imply inclusion, concatenation or reading order; following one may replace or supplement the current view. This specification defines no content-inclusion mechanism.

**Consumers MAY:**

- Present the entry point and the Markdown files it links to as one unified view
- Produce a single rendered output from them (for example, for printing or export)

This is the default mode and applies when no manifest is present or when `manifest.mode` is `"document"`.

#### 5.7.3 Project Mode

`project` mode indicates that the archive represents a **collection of independent Markdown documents** with navigational relationships between them.

**Requirements:**

- A `manifest.json` file MUST be present
- The manifest MUST declare `"mode": "project"`
- The manifest SHOULD define a valid `entryPoint` (conforming producers MUST; see [Section 14.1](#141-conforming-producer))

**Consumers MUST:**

- Treat each Markdown file as a separate document that can be addressed and opened on its own
- NOT flatten or merge Markdown files into a single logical document

**Consumers MAY:**

- Provide navigation UI (for example, a sidebar or table of contents)
- Support cross-document linking
- Allow users to open any file directly, not only the entry point

> **Note on navigation structure:** This specification does not define ordered navigation, pagination, or table-of-contents layout. `project` mode establishes that documents MUST be preserved as separate units; it does not mandate how consumers surface navigation to users.

#### 5.7.4 Entry Point Semantics by Mode

In `document` mode:

- Entry point is resolved using the standard discovery algorithm (Section 5.5)

In `project` mode:

- If `manifest.entryPoint` is present, it MUST be used as the primary entry point, subject to rule 1 of [Section 5.5](#55-entry-point-discovery) when the value is invalid or matches no file
- If `manifest.entryPoint` is absent, consumers MUST apply the standard discovery algorithm
- Consumers MUST NOT arbitrarily select a file when no unambiguous entry point can be determined

#### 5.7.5 Unrecognized Mode Values

If `manifest.mode` contains a value not recognized by the consumer (for example, a value defined in a future spec version), the consumer:

- MUST NOT silently fall back to `document` mode
- SHOULD fail with error `ERR_MODE_UNSUPPORTED` and report the unrecognized value
- MAY offer the user a choice to proceed in `document` mode as an explicit override

This preserves the spec's principle that consumers MUST NOT rely on heuristics to infer structure.

#### 5.7.6 Consumer Support Levels

Consumers MAY support one or both modes:

- **Document-only consumers** MUST support `document` mode. When encountering `project` mode, they MAY fall back to `document` mode provided they emit a clear warning that `project` mode is not supported and the archive will be treated as a single document. They MAY instead fail with `ERR_MODE_UNSUPPORTED`. Silent fallback without any warning is NOT permitted.
- **Full-featured consumers** SHOULD support both modes.

A consumer MUST NOT silently render an archive incorrectly when it encounters a mode it cannot handle. For **unrecognized** mode values (values not defined in this spec), consumers MUST NOT fall back silently and SHOULD fail with `ERR_MODE_UNSUPPORTED`. For **recognized but unsupported** modes (e.g. a document-only consumer encountering `project`), warn-and-fallback to `document` is conforming provided the warning is user-visible; the consumer need not ask the user before falling back.

### 5.8 Agent-Facing `AGENTS.md` (Optional)

Producers **MAY** include a root-level `AGENTS.md` addressed to AI agents and other automated tools that encounter the archive without native `.mdz` support. Where `README.md` ([Section 5.6](#56-human-facing-readmemd-optional)) tells a person how to open the package, `AGENTS.md` tells a tool how to handle it safely.

When present, `AGENTS.md` **SHOULD** briefly include:

- what the archive is (`.mdz` / MDZip) and where to find format documentation,
- a preference for archive-aware access (for example, an MDZip MCP server, library or compatible tool) over extracting or rewriting the archive with generic ZIP tools,
- how to locate the entry point (the algorithm in [Section 5.5](#55-entry-point-discovery), including that support files are set aside),
- how to interpret `manifest.mode` ([Section 5.7](#57-mode-semantics)),
- that the archive should not be modified with generic ZIP tools without the user's agreement: they don't apply MDZip's rules (such as keeping the entry point resolvable) and can't detect a conflicting edit made in another tool.

`AGENTS.md` is advisory: nothing in it overrides `manifest.json`, which is authoritative when present, or the rules of this specification. Like `README.md`, `AGENTS.md` does not affect conformance logic, and it is a support file for entry point discovery ([Section 5.5](#55-entry-point-discovery)).

A reusable sample is available at [`examples/templates/AGENTS.sample.md`](examples/templates/AGENTS.sample.md).

---

## 6. Manifest File

The manifest file, when present, **MUST** be named `manifest.json` and placed at the root of the archive. It **MUST** be a valid [JSON](https://www.rfc-editor.org/rfc/rfc8259) document encoded in UTF-8.

The manifest requirement depends on role:

- Conforming **producers** **MUST** write `manifest.json` in every archive they create, with at least the fields listed in [Section 14.1](#141-conforming-producer). This applies to software only; a person zipping a folder by hand is not a producer.
- Conforming **consumers** **MUST NOT** require `manifest.json`. An archive without one is valid and is resolved with the entry point discovery algorithm ([Section 5.5](#55-entry-point-discovery)) and the defaults in [Section 5.7.1](#571-mode-defaults) and [Section 11.3](#113-manifests-without-version-metadata).

Producer tools **MAY** accept non-JSON authoring inputs (for example, JSON5) as a local convenience, but conforming `.mdz` archives **MUST** contain `manifest.json` serialized as standard JSON per RFC 8259.

A versioned JSON Schema companion for this release is available at [`schema/manifest-1.2.0.schema.json`](schema/manifest-1.2.0.schema.json). It validates manifests written by a conforming producer, so it requires `spec.version` and `entryPoint` and checks that `entryPoint` is a valid entry point path ([Section 5.5](#55-entry-point-discovery)); consumers **MUST NOT** use it to reject archives. Schemas for earlier releases remain in `schema/`. The prose specification remains normative when differences exist.

### 6.1 Schema

```json
{
  "spec": {
    "name": "mdzip-spec",
    "version": "<spec version>"
  },
  "producer": {
    "application": {
      "name": "<application/tool name>",
      "version": "<application version>",
      "url": "<application URL>"
    },
    "core": {
      "name": "<core library/runtime name>",
      "version": "<core library/runtime version>",
      "url": "<core library/runtime URL>"
    }
  },
  "author": {
    "name": "<author name>",
    "email": "<author email>",
    "url": "<author URL>"
  },
  "title": "<document title>",
  "mode": "<interpretation mode>",
  "entryPoint": "<path to entry point markdown file>",
  "language": "<BCP 47 language tag>",
  "description": "<short description>",
  "version": "<document version>",
  "created": {
    "when": "<RFC 3339 datetime>",
    "by": {
      "name": "<creator name>",
      "email": "<creator email>",
      "url": "<creator URL>"
    }
  },
  "modified": {
    "when": "<RFC 3339 datetime>",
    "by": {
      "name": "<modifier name>",
      "email": "<modifier email>",
      "url": "<modifier URL>"
    }
  },
  "license": "<SPDX license identifier or URL>",
  "keywords": ["<keyword>"],
  "cover": "<path to cover image asset>"
}
```

`created` and `modified` each take one of two forms:

- an object with a required `when` and an optional `by` — the current form, which producers **SHOULD** write; or
- a plain datetime string — the legacy form from draft `1.0.x`.

Datetimes in both forms **MUST** use the [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) `date-time` format, the profile of ISO 8601 used by JSON Schema — for example `2026-03-08T14:30:00Z` or `2026-03-08T09:30:00-05:00`. A value in another ISO 8601 form is invalid and, like other descriptive fields, ignored ([Section 6.4](#64-manifest-validation)).

Consumers **MUST** accept both forms, whatever the archive's `spec.version`, including when it has none.

> **Required fields:** none for arbitrary hand-authored manifests.  
> For **conforming producer-generated** manifests, `spec.version` and `entryPoint` are REQUIRED, and `title` and `mode` are RECOMMENDED (see [Section 14.1](#141-conforming-producer)).

### 6.2 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `spec` | object | OPTIONAL | Container for spec compatibility metadata. |
| `spec.name` | string | OPTIONAL | Identifier for the target specification (e.g., `"mdzip-spec"`). |
| `spec.version` | string | CONDITIONALLY REQUIRED | The version of this specification the file conforms to. **MUST** be a [Semantic Versioning 2.0.0](https://semver.org/) string (e.g., `"1.2.0"`). **REQUIRED** when `manifest.json` is emitted by a conforming producer. |
| `producer` | object | OPTIONAL | Producer provenance metadata. |
| `producer.application` | object | OPTIONAL | User-facing tool/application that generated the archive. |
| `producer.application.name` | string | OPTIONAL | Application/tool display name. |
| `producer.application.version` | string | OPTIONAL | Application/tool version string. |
| `producer.application.url` | string | OPTIONAL | URL for producer application homepage/repository. Producers **SHOULD** include when stable and available. |
| `producer.core` | object | OPTIONAL | Underlying reusable core library/runtime used by the producer application. |
| `producer.core.name` | string | OPTIONAL | Core library/runtime name. |
| `producer.core.version` | string | OPTIONAL | Core library/runtime version string. |
| `producer.core.url` | string | OPTIONAL | URL for core library/runtime homepage/repository. Producers **SHOULD** include when stable and available. |
| `author` | object | OPTIONAL | Human/content author attribution metadata. |
| `author.name` | string | OPTIONAL | Author display name. |
| `author.email` | string | OPTIONAL | Author contact address. Producers **SHOULD** include when available and appropriate to disclose. |
| `author.url` | string | OPTIONAL | Author website/profile URL. Producers **SHOULD** include when available and appropriate to disclose. |
| `title` | string | OPTIONAL | The human-readable title of the document. If present, it **MUST NOT** be empty. If omitted, consumers **SHOULD** derive a display title from available context (for example, the entry-point, filename or first heading). Conforming producers **SHOULD** include it. |
| `mode` | string | OPTIONAL | The interpretation mode of the archive. Allowed values: `"document"` (default), `"project"`. Values are case-sensitive and MUST be lowercase. If absent, consumers MUST assume `"document"`. If present with an unrecognized value (including incorrect casing such as `"Document"` or `"PROJECT"`), consumers MUST NOT silently fall back to `document` mode. MUST be `"project"` when the archive is a collection of independent documents ([Section 5.7.3](#573-project-mode)); a single publication split across several files is `"document"`. Conforming producers **SHOULD** include it explicitly, including `"document"`. See [Section 5.7](#57-mode-semantics). |
| `entryPoint` | string | CONDITIONALLY REQUIRED | Path to the primary Markdown file, relative to the archive root (e.g., `"chapters/start.md"`). **MUST** be a valid entry point path as defined in [Section 5.5](#55-entry-point-discovery) (a relative `.md`/`.markdown` file path satisfying Section 5.4), and the referenced file **MUST** exist in the archive, matched as described in [Section 5.4.1](#541-path-matching). Consumers report a malformed value as `ERR_ENTRYPOINT_INVALID` and a valid but absent one as `ERR_ENTRYPOINT_MISSING`. **REQUIRED** when `manifest.json` is emitted by a conforming producer. If omitted, consumers apply the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery). |
| `language` | string | OPTIONAL | The natural language of the document as a [BCP 47](https://www.rfc-editor.org/rfc/rfc5646) language tag (e.g., `"en"`, `"fr-CA"`). If omitted, the language is unspecified: consumers **MAY** fall back to a default of their choice, such as the user's interface language or `"en"`, but **SHOULD NOT** state it as the document's language (for example, when exposing it to assistive technology). |
| `description` | string | OPTIONAL | A short plain-text description of the document. |
| `version` | string | OPTIONAL | The version of the document itself (not the spec version). **SHOULD** follow Semantic Versioning. |
| `created` | object or string | OPTIONAL | Creation metadata: an object with `when` (current form) or an RFC 3339 datetime string (legacy draft `1.0.x` form); consumers **MUST** accept both (Section 6.1). |
| `created.when` | string | CONDITIONALLY REQUIRED | Required when `created` is an object. The creation datetime, in RFC 3339 `date-time` format. |
| `created.by` | object | OPTIONAL | Creator identity metadata when known and appropriate to disclose. |
| `created.by.name` | string | OPTIONAL | Creator display name. |
| `created.by.email` | string | OPTIONAL | Creator contact address. |
| `created.by.url` | string | OPTIONAL | Creator website/profile URL. |
| `modified` | object or string | OPTIONAL | Last-modified metadata: an object with `when` (current form) or an RFC 3339 datetime string (legacy draft `1.0.x` form); consumers **MUST** accept both (Section 6.1). |
| `modified.when` | string | CONDITIONALLY REQUIRED | Required when `modified` is an object. The last-modified datetime, in RFC 3339 `date-time` format. |
| `modified.by` | object | OPTIONAL | Modifier identity metadata when known and appropriate to disclose. |
| `modified.by.name` | string | OPTIONAL | Modifier display name. |
| `modified.by.email` | string | OPTIONAL | Modifier contact address. |
| `modified.by.url` | string | OPTIONAL | Modifier website/profile URL. |
| `license` | string | OPTIONAL | An [SPDX license identifier](https://spdx.org/licenses/) (e.g., `"MIT"`, `"CC-BY-4.0"`) or a URL pointing to the license text. |
| `keywords` | array of strings | OPTIONAL | A list of keywords or tags describing the document. |
| `cover` | string | OPTIONAL | Archive-root-relative path to a cover image asset (e.g., `"images/cover.png"`). It **MUST** be a relative archive path satisfying [Section 5.4](#54-path-constraints) that names a file (no trailing `/`); as with `entryPoint`, a single leading `./` is permitted and removed before matching ([Section 5.4.1](#541-path-matching)). It **MUST** reference an existing file in the archive. If `cover` is invalid or the referenced file is missing, conforming consumers **SHOULD** ignore `cover` and continue processing the archive; they **MAY** emit a warning. |

### 6.3 Additional Fields

Conforming producers **MAY** include additional fields not defined in this specification. Conforming consumers **MUST** ignore any unrecognized fields.

A producer that rewrites an existing `manifest.json` **MUST** preserve every field it does not recognize, unless the user explicitly asks for it to be removed. This applies at the top level and inside recognized objects (for example, an unrecognized property within `producer` or `author`), and to every JSON value type: object, array, string, number, boolean and `null`. Fields may have been added by a newer version of this specification, a profile or another tool; dropping them silently loses data the producer cannot see.

Preservation is semantic, not textual: the preserved value **MUST** be equal, as JSON, to the original, but whitespace, indentation and property order may change. A producer that deserializes the manifest into a closed, typed model **MUST** retain unrecognized data alongside it (or merge it back before saving), rather than serializing only the fields it knows.

### 6.4 Manifest Validation

A consumer that finds `manifest.json` validates it as follows.

**Unreadable manifests.** If the manifest is not valid UTF-8, is not valid JSON ([RFC 8259](https://www.rfc-editor.org/rfc/rfc8259)), or its top-level value is not an object, it is invalid. The consumer **MUST** report `ERR_MANIFEST_INVALID` and **MUST NOT** silently ignore the manifest. It **MAY** offer to continue as if the archive had no manifest, after a visible warning.

**Fields.** The fields defined in [Section 6.2](#62-field-definitions) are either *critical*, because they change how the archive is interpreted, or *descriptive*. A field present with the wrong type or an invalid value is handled by kind:

| Kind | Fields | When the value is wrong |
|---|---|---|
| Critical | `spec`, `spec.version`, `mode`, `entryPoint` | An error; consumers **MUST NOT** ignore it. A `spec` that is not an object, or a `spec.version` that is not a Semantic Versioning string, is `ERR_MANIFEST_INVALID`. A `mode` that is a string the consumer doesn't recognize is `ERR_MODE_UNSUPPORTED` ([Section 5.7.5](#575-unrecognized-mode-values)); any other non-string `mode` is `ERR_MANIFEST_INVALID`. An invalid `entryPoint` is `ERR_ENTRYPOINT_INVALID` ([Section 5.5](#55-entry-point-discovery)). |
| Descriptive | Every other field in Section 6.2, for example `title`, `author`, `language`, `created` and `cover` | Consumers **SHOULD** ignore the field and **MAY** warn; the archive still opens. |

`null` is a wrong type, not an absent field: `{"spec": null}` is invalid. Unrecognized fields are never validated ([Section 6.3](#63-additional-fields)). A missing `cover` file is tolerated while a missing `entryPoint` file is not for the same reason: `cover` is descriptive, `entryPoint` is critical.

**Duplicate member names.** Two members with the same name in one object (for example two `"title"` members) make the manifest ambiguous, and RFC 8259 leaves their meaning undefined. Producers **MUST NOT** write duplicate member names. Consumers **SHOULD** report them; a consumer that accepts such a manifest **MUST** use the last occurrence, which is what common JSON parsers do.

### 6.5 Example Manifests

#### Document Mode (default — `mode` may be omitted in hand-authored manifests; producers should include it)

```json
{
  "spec": {
    "name": "mdzip-spec",
    "version": "1.2.0"
  },
  "producer": {
    "application": {
      "name": "mdzip-cli",
      "version": "1.2.0",
      "url": "https://example.com/mdzip-cli"
    },
    "core": {
      "name": "mdzip-core",
      "version": "0.9.4",
      "url": "https://example.com/mdzip-core"
    }
  },
  "author": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "url": "https://example.com/~jane"
  },
  "title": "My Technical Guide",
  "mode": "document",
  "entryPoint": "index.md",
  "language": "en",
  "description": "A comprehensive guide to building widgets.",
  "version": "2.1.0",
  "created": {
    "when": "2026-01-15T09:00:00Z",
    "by": {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "url": "https://example.com/~jane"
    }
  },
  "modified": {
    "when": "2026-03-08T14:30:00Z",
    "by": {
      "name": "Jane Smith",
      "email": "jane@example.com",
      "url": "https://example.com/~jane"
    }
  },
  "license": "CC-BY-4.0",
  "keywords": ["widgets", "guide", "tutorial"],
  "cover": "images/cover.png"
}
```

#### Project Mode

```json
{
  "spec": {
    "name": "mdzip-spec",
    "version": "1.2.0"
  },
  "producer": {
    "application": {
      "name": "mdzip-cli",
      "version": "1.3.0",
      "url": "https://example.com/mdzip-cli"
    }
  },
  "title": "My Documentation Site",
  "mode": "project",
  "entryPoint": "index.md",
  "language": "en"
}
```

---

## 7. Markdown Content Files

### 7.1 Encoding

All Markdown files inside the archive **MUST** be encoded in UTF-8.

### 7.2 Markdown Dialect

This specification does not mandate a specific Markdown dialect. Producers **SHOULD** note in the manifest `description` or within the document itself which dialect is used (e.g., [CommonMark](https://commonmark.org/), [GitHub Flavored Markdown](https://github.github.com/gfm/)).

### 7.3 File Extensions

Markdown files **SHOULD** use the `.md` file extension. The `.markdown` extension is also permitted. Consumers **MUST** recognize both extensions ASCII case-insensitively (so `NOTES.MD` is a Markdown file); see [Section 5.4.1](#541-path-matching).

### 7.4 Multiple Pages

An `.mdz` archive **MAY** contain multiple Markdown files, allowing a document to be split across chapters, sections, or pages. The primary document is the entry point, determined by the discovery algorithm in [Section 5.5](#55-entry-point-discovery) (by convention `index.md`). Other Markdown files **SHOULD** be linked from the primary document or from other Markdown files within the archive using relative paths.

---

## 8. Asset Files

Asset files are the non-Markdown files the archive uses (see the definition in [Section 3](#3-terminology)), such as images, stylesheets, fonts, data files, schemas or templates. A file can be used without any Markdown link to it — a `cover` image, or a data file read by an extension.

### 8.1 Placement

Assets **SHOULD** be organized in named subdirectories at the archive root, grouped by type (e.g., `images/`, `styles/`, `fonts/`, `pdf/`). Additional hierarchy within those directories is **RECOMMENDED** when the volume of files warrants it. A dedicated `assets/` parent directory **MAY** be used to group all asset directories together, but is not required.

### 8.2 Allowed Asset Types

There is no restriction on asset file types.

### 8.3 Unused Assets

Conforming producers **SHOULD NOT** include files the archive does not use: files that nothing in the archive references and that no declared extension needs, such as leftovers from an editor or build. A file that is not linked from Markdown is not unused for that reason alone. Producers modifying an archive keep files they don't recognize ([Section 14.1](#141-conforming-producer)); deciding what is unused is a creation-time choice.

---

## 9. Linking and References

### 9.1 Internal Links

References to other files within the archive (Markdown files and assets) **MUST** use **relative paths** based on the location of the referencing file within the archive.
Relative links **MAY** include `../` segments. A link whose resolved path stays within the archive root is an *internal link*; one that climbs above the archive root is a link outside the archive ([Section 9.4](#94-links-outside-the-archive-optional)).

**Example:** A Markdown file at the archive root (`index.md`) referencing an image:
```markdown
![Diagram](images/diagram.svg)
```

**Example:** A Markdown file in a subdirectory (`chapters/intro.md`) referencing an image at the archive root:
```markdown
![Logo](../images/logo.png)
```

### 9.2 External Links

Links to external URLs (e.g., `https://example.com`) are permitted. Conforming consumers **MAY** choose to warn users before following external links. A destination with a URL scheme (such as `https:` or `mailto:`) is an external URL and is not resolved as a path.

A document can also load an external resource automatically, such as an image written `![logo](https://example.com/logo.png)`. Fetching it tells that server the document was opened, and the archive is no longer self-contained ([Section 1](#1-overview)): the resource can change or disappear, and it does not load offline.

- Consumers **SHOULD** let the user turn off automatic loading of external resources.
- Consumers **SHOULD NOT** automatically load external resources over unencrypted `http:`.
- Producers and validators **MAY** report external resources as informational notices, as for links outside the archive ([Section 9.6](#96-security-and-portability-of-links-beyond-an-archive)), not as errors.

### 9.3 Path Resolution

This section and Sections 9.4–9.5 apply to **standard Markdown link destinations**: inline and reference-style links and images (`[text](path)`, `![alt](path)`, `[text][ref]` with `[ref]: path`) and the `href` and `src` attributes of HTML elements embedded in Markdown. Other link syntaxes, such as wikilinks, are covered by [Section 9.7](#97-other-link-syntaxes).

Conforming consumers **MUST** resolve relative paths against the path of the referencing file within the archive, using this algorithm:

1. Split the destination at its first `#`. What follows is the *fragment*: it identifies an anchor in the target document, does not take part in path resolution, and keeps any `?` it contains (`page.md#heading?text` has the fragment `heading?text`). Then remove any `?query` from the part before the `#`. A query has no meaning in this specification; consumers **MAY** keep it for presentation but **MUST NOT** use it to choose the target.
2. If what remains is empty (`#usage`, `?view=print`), the link refers to the referencing document itself.
3. If the destination begins with `/` or contains `\`, it is not a valid relative link; treat it as unresolved.
4. Split the destination into segments on `/`, then percent-decode each segment as UTF-8, exactly once; for example, `Mary%20Shelley/Frankenstein.md` has the segments `Mary Shelley` and `Frankenstein.md`, and `%252e%252e` decodes to the literal name `%2e%2e`, not to `..`. A segment with invalid percent-encoding (`%ZZ`, or bytes that are not valid UTF-8 such as `%C3%28`) makes the link unresolved. A segment that decodes to text containing `/`, `\` or a control character makes the link unresolved, so an encoded separator such as `%2F` cannot introduce a path step. A decoded `#` or `?` (from `%23` or `%3F`) is part of the name, not a delimiter.
5. Starting from the directory of the referencing file, apply the segments in order: `.` (or one that decodes to `.`) and an empty segment (from `//`) stay in the current directory, `..` (or one that decodes to `..`) moves up one directory, and any other segment moves into that name. A destination that ends in `/` names a directory: inside an archive, where entries are files, it is unresolved; outside one, it is resolved only where [Section 9.5](#95-links-into-archives-optional) allows a link to end at an archive.
6. If every step stays within the archive, the result is an internal link: match the resulting path against archive entries as described in [Section 5.4.1](#541-path-matching).
7. If a `..` step would move above the archive root, the link leaves the archive and is resolved as described in [Section 9.4](#94-links-outside-the-archive-optional).

The base is always the referencing file's location: an HTML `<base>` element in a document does not change how its links resolve.

This specification does not define how a heading becomes an anchor. Markdown dialects differ (`## My Heading` is `#my-heading` on GitHub and `#My Heading` in Obsidian), so whether a fragment matches a heading depends on the consumer's dialect ([Section 12.4](#124-markdown-dialect-portability)). A fragment that matches no anchor still leaves the link resolved to its target document.

Link resolution is separate from archive entry path validation. The archive's own entry names **MUST** still satisfy [Section 5.4](#54-path-constraints) — an entry named `../escape.md` remains invalid — and nothing in this section relaxes the extraction rules in [Section 13.1](#131-archive-handling).

A link that cannot be resolved **MUST** be treated as unresolved: the consumer **MAY** indicate it to the user (for example, by styling it as a broken link) but **MUST NOT** substitute a different target. In particular, a consumer **MUST NOT** clamp a `..` step at the archive root and resolve the rest of the link inside the archive.

### 9.4 Links Outside the Archive (Optional)

A relative link can climb above the archive root to reach files stored next to the `.mdz` file, for example to link a packaged document to other notes in the same folder. For resolution, the archive root is treated as a virtual directory located where the `.mdz` file is: the directory containing the archive is its parent.

Example: a folder `MyVault/` contains `Notes.md`, `References/Design.md` and `Project.mdz`, and the archive contains `index.md` and `chapters/intro.md`.

| Referencing file | Link | Target |
|---|---|---|
| `index.md` | `../Notes.md` | `MyVault/Notes.md` |
| `index.md` | `../References/Design.md` | `MyVault/References/Design.md` |
| `chapters/intro.md` | `../../Notes.md` | `MyVault/Notes.md` |
| `chapters/intro.md` | `../index.md` | `index.md`, inside the archive (an internal link) |

Rules:

- Support is **OPTIONAL**. A consumer that does not support links outside the archive **MUST** treat them as unresolved. Supporting them does not affect any other conformance requirement.
- A consumer that supports them resolves the remaining segments against the directory containing the `.mdz` file, using the host's normal path and filesystem rules. Path matching on the host follows the host filesystem (which may ignore case or normalize Unicode); [Section 5.4.1](#541-path-matching) governs matching only inside archives.
- If the consumer has no host filesystem location for the archive — for example, the archive was opened from bytes in a web browser, an email attachment or a download stream — links outside the archive **MUST** be treated as unresolved, not mapped to a guessed location.
- If the target is outside the consumer's trust boundary ([Section 9.6](#96-security-and-portability-of-links-beyond-an-archive)), does not exist, or the host denies access, the link is unresolved.
- If a segment of the remaining path names an MDZip archive, the link enters that archive and is resolved as described in [Section 9.5](#95-links-into-archives-optional).

These links apply to any link destination — documents, images and other assets — but resources that a document loads automatically (such as `![logo](../logo.png)`) are unresolved by default ([Section 9.6](#96-security-and-portability-of-links-beyond-an-archive)).

### 9.5 Links Into Archives (Optional)

A relative link can address a document inside an `.mdz` archive by treating the archive as a directory, both from an ordinary Markdown file next to the archive and from a link that has left another archive ([Section 9.4](#94-links-outside-the-archive-optional)). Continuing the example in Section 9.4, from `MyVault/Notes.md`:

```markdown
[Design notes](Project.mdz/chapters/intro.md)
[Introduction section](Project.mdz/chapters/intro.md#background)
[Project](Project.mdz)
```

Rules:

- Support is **OPTIONAL**. A consumer that does not support links into archives **MUST** treat them as unresolved.
- While resolving on the host, a segment whose name has an `.mdz` extension (ASCII case-insensitive) becomes an archive boundary only when it names an existing file that the consumer can open as an MDZip archive. A directory that happens to be named `Something.mdz` is an ordinary directory.
- The segments after the boundary form a path inside that archive. Apply `.` and `..` within it; a `..` above that archive's root makes the link unresolved. Match the result against the archive's entries as described in [Section 5.4.1](#541-path-matching).
- A link that ends at the archive itself (`Project.mdz`, optionally with a trailing `/`) opens the document selected by entry point discovery ([Section 5.5](#55-entry-point-discovery)); a fragment then applies to that document.
- A link **MUST NOT** enter more than one archive boundary. Leaving the referencing archive (Section 9.4) does not count as entering one, but a link that names an archive inside another archive (such as `Outer.mdz/inner.mdz/index.md`) is unresolved.
- A link that enters the archive containing the referencing file (for example, `../Project.mdz/chapters/intro.md` from inside `Project.mdz`) refers to the same entry as the corresponding internal link.
- Links into archives use ordinary relative Markdown links; this specification defines no URI scheme for them. Renderers that do not support them will show these links as broken.

When a consumer needs an identifier for a document inside an archive, for example to build backlinks or a link graph, it **SHOULD** use the archive's host path followed by the entry path, such as `MyVault/Project.mdz/chapters/intro.md`. This identifies the document at its current location on the host; it changes when the archive or its folder is moved or renamed.

### 9.6 Security and Portability of Links Beyond an Archive

An archive may come from anyone, so a link that leaves it is a request, written by the archive's author, to reach files on the reader's machine. The risk is disclosure as well as modification: an untrusted archive can try to display or reveal local files, for example with `![](../../.ssh/id_rsa)`.

- Resolving or following a link outside an archive or into another archive is **read-only**. It **MUST NOT** extract files to the host filesystem, write to it, or modify any archive.
- **Trust boundary.** A consumer that supports these links **MUST** limit them to a *trust boundary*: a location the user has chosen to trust, such as the workspace or vault an editor has open. A target outside it **MUST** be treated as unresolved, whether or not it exists, unless the user explicitly allows access to that target (for example by confirming a prompt that names it). A consumer with no such location, such as a viewer opening a single file, has no trusted targets outside the archive. The host's own access controls apply as well.
- **Navigation and automatic loading.** *Navigation* (the user follows a link) and *automatic loading* (the consumer fetches a resource the document displays, such as an image, stylesheet or embedded file) are different uses. Automatic loading from outside the archive **MUST** be off by default. A consumer **MAY** enable it for targets inside the trust boundary when the user or the host's configuration asks for it, and **MUST NOT** enable it for targets outside the boundary.
- Consumers **SHOULD** show the user where a navigation link outside the archive leads before opening it, unless the target is inside the trust boundary.
- Archives that rely on links outside the archive are **not self-contained**: those links resolve only while the archive sits next to the files it references, and break when the archive is moved, shared or opened in a browser. Authors opt into this deliberately; content that must travel with the document belongs inside the archive.
- Producers **MUST NOT** rewrite links outside the archive into internal links, or vice versa, without the author's request. Validators and producers **SHOULD** report links outside the archive as informational notices (for example, "this archive links to 3 files outside it"), not as errors.

### 9.7 Other Link Syntaxes

This specification does not prohibit or restrict other hyperlink syntaxes. Markdown dialects and host applications define their own, such as wikilinks (`[[Page]]`, `[[Page#Heading|label]]`) and embeds (`![[image.png]]`) in Obsidian, Foam and similar tools. Archives **MAY** contain them, and consumers **MAY** support them using the resolution rules of the dialect or host that defines them, including looking up a page by name rather than by path. Sections 9.3–9.5, including the rule against substituting a different target, govern only standard Markdown link destinations.

For links in these syntaxes:

- Consumers that support a syntax that looks pages up by name **SHOULD** consider the documents inside the archive before looking further, so that links between an archive's own documents work the same in every host that supports the syntax.
- Consumers that don't support a syntax **SHOULD** leave its text intact, both when displaying it (show it as written rather than dropping it) and when saving (Section 14.1 already requires untouched content to be preserved).
- The security and portability rules of [Section 9.6](#96-security-and-portability-of-links-beyond-an-archive) still apply when such a link reaches outside the archive: resolving or following it is read-only and stays within the host's trust boundaries.

These syntaxes are dialect-specific, and a renderer that doesn't know them shows them as plain text. Producers relying on them **SHOULD** say so, as described in [Section 12.4](#124-markdown-dialect-portability); producers that need links to work everywhere **SHOULD** use standard Markdown links.

---

## 10. MIME Type and File Extension

| Property | Value |
|----------|-------|
| **File extension** | `.mdz` |
| **MIME type** | Proposed `application/vnd.mdzip` |

Producers and consumers **SHOULD** use the `.mdz` file extension. The proposed MIME type `application/vnd.mdzip` **SHOULD** be used when the format is transmitted over HTTP or identified in metadata.

`application/vnd.mdzip` is currently an unregistered vendor media type in this specification. Until formal registration is completed, implementations **MAY** treat it as provisional for interoperability testing. For broad interoperability, servers **MAY** use `application/zip` or `application/octet-stream` as a fallback until `application/vnd.mdzip` is more widely recognized.

---

## 11. Versioning

### 11.1 Specification Versioning

This specification uses [Semantic Versioning 2.0.0](https://semver.org/):

- **Major version** increments indicate breaking, backwards-incompatible changes to the format.
- **Minor version** increments indicate backwards-compatible additions or clarifications.
- **Patch version** increments indicate corrections or editorial changes with no impact on format compatibility.

Compatibility is defined in terms of archives, not implementations. Within a major version, an archive valid under an earlier minor version stays readable by a consumer of a later one, and an archive written to a later minor version stays usable by an earlier consumer, which ignores what it doesn't recognize. A minor version can add requirements on implementations (for example, 1.2.0 requires producers to write a manifest), so software that conforms to one minor version does not automatically conform to the next.

### 11.2 Manifest `spec.version` Field

When `manifest.json` includes `spec.version`, it identifies the version of this specification that the producing tool targeted. Conforming consumers:

- **MUST** reject files where `spec.version` major version is higher than the highest major version the consumer supports.
- **SHOULD** warn users when `spec.version` major version is lower than the consumer's current major version support.
- **MUST NOT** reject a file solely because its `spec.version` minor or patch version differs from the consumer's supported version, provided the major version is supported. This does not promise that every feature renders; an archive can still fail for other reasons, such as an unsupported mode ([Section 5.7.6](#576-consumer-support-levels)).

### 11.3 Manifests Without Version Metadata

Conforming consumers **MUST NOT** assume that all manifests are producer-generated. If `spec.version` is absent (whether `manifest.json` is absent or present but missing `spec.version`), conforming consumers:

- **MUST** treat the archive as compatible with baseline 1.x behavior defined by this specification.
- **MUST NOT** reject the archive solely due to missing version metadata.
- **SHOULD** expose that version metadata is unavailable when presenting document details to users.

---

## 12. Compatibility Notes

This section summarizes expected behavior that improves interoperability across tools, platforms, and Markdown ecosystems.

### 12.1 Baseline Interoperability

- Conforming consumers **MUST** implement the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery).
- Conforming consumers **MUST** support UTF-8 encoded Markdown and JSON files.
- Conforming consumers **MUST** support relative path resolution semantics defined in [Section 9](#9-linking-and-references).

### 12.2 Line Endings

- Conforming producers **SHOULD** write LF (`\n`) line endings in Markdown files and `manifest.json` that they create or modify, converting CRLF (`\r\n`) from the source content if needed. Markdown treats both as line endings, so the conversion does not change the document's meaning, and no warning is required.
- Conforming producers **SHOULD NOT** change line endings in other files unless the user asks. Some formats depend on them, for example CRLF in Windows batch files or in CSV files that follow RFC 4180.
- Conforming producers **MUST NOT** change line endings in entries they do not otherwise modify ([Section 14.1](#141-conforming-producer)).
- Conforming producers **MAY** offer an option to keep the original line endings.
- Conforming consumers **MUST** accept text files using LF (`\n`) and CRLF (`\r\n`) line endings.

This specification does not define a manifest field for line endings: consumers accept both, and line endings can differ from file to file. Tools that extract archives **MAY** offer to convert line endings for the target platform.

### 12.3 Path and Case Behavior

- Paths inside archives **MUST** use forward slashes (`/`), regardless of host platform.
- Consumers **MUST** match archive paths case-sensitively after NFC normalization, as described in [Section 5.4.1](#541-path-matching), for deterministic behavior across operating systems and languages.
- Unknown manifest fields **MUST** be ignored to preserve forward compatibility.

### 12.4 Markdown Dialect Portability

- Producers **SHOULD** prefer portable Markdown constructs that degrade gracefully in CommonMark-class renderers.
- Producers **SHOULD** document non-portable syntax expectations when relying on dialect-specific features, such as wikilinks or other link syntaxes ([Section 9.7](#97-other-link-syntaxes)).

---

## 13. Security Considerations

Conforming consumers and producers should treat `.mdz` content as potentially untrusted input. The following controls are recommended to reduce risk.

### 13.1 Archive Handling

- Consumers **MUST** reject archive entries whose paths would resolve outside the archive root after normalization (e.g., absolute paths or relative paths that escape the root), and **MUST NOT** write any file outside the intended destination when extracting. This concerns entry names inside the ZIP; Markdown links that point outside the archive are resolved separately and never trigger extraction ([Section 9.4](#94-links-outside-the-archive-optional), [Section 9.6](#96-security-and-portability-of-links-beyond-an-archive)).
- Entries whose paths violate [Section 5.4](#54-path-constraints) are non-conforming. Consumers **MUST NOT** extract them under their stored names, and **MUST NOT** silently rename them or resolve a link to a renamed copy, since renaming changes an entry's identity and can create new collisions. Consumers **SHOULD** reject such an archive (`ERR_PATH_INVALID`); they **MAY** offer an explicit recovery, such as skipping the entries or extracting them under names the user approves.
- Consumers **SHOULD** enforce limits on extracted entry count, total uncompressed bytes, and compression ratio to mitigate ZIP bomb attacks.
- Consumers **MUST NOT** follow a symbolic link entry ([Section 4](#4-file-format)): they **MUST NOT** create it as a link when extracting, and **MUST NOT** resolve a path or a Markdown link through it, even when its target lies inside the archive. They **SHOULD** report it, and **MAY** skip it or read it as an ordinary file whose content is the stored target text. The same applies to hard links and other special files if the ZIP library exposes them.
- Consumers **MUST NOT** choose between two entries whose paths are equal after NFC normalization, or between a file and a directory with the same path ([Section 5.4](#54-path-constraints)). They **SHOULD** reject the archive with `ERR_DUPLICATE_PATH` or `ERR_PATH_CONFLICT` respectively.
- Consumers extracting to a filesystem that is case-insensitive or normalizes Unicode **SHOULD** detect entries that would collide there and report them, rather than letting one silently overwrite another.

### 13.2 Content Handling

- Consumers **MUST NOT** execute scripts or binaries from `.mdz` content as part of normal rendering.
- Consumers **SHOULD** warn before opening external URLs found in document links.
- Consumers **SHOULD** let users turn off automatic loading of external resources such as remote images, which reveals to their servers that the document was opened ([Section 9.2](#92-external-links)).
- Consumers **SHOULD** apply implementation-specific size/time limits while parsing large Markdown or metadata files.

### 13.3 Producer Guidance

- Producers **SHOULD NOT** include credentials, private keys, or other secrets in archive content.
- Producers **SHOULD** include only files the archive uses ([Section 8.3](#83-unused-assets)), so that unrelated local files are not shared by accident.

---

## 14. Conformance

### 14.1 Conforming Producer

A conforming producer is any software that writes `.mdz` files. Each of its operations is either a *creation* (writing a new archive, for example by packing a folder or converting a document) or a *modification* (changing an existing archive and saving it). A creation **MUST** satisfy the list below. A modification **MUST** satisfy the second list; the archive it writes **MUST** also meet item 1 below, and every entry it adds or rewrites items 7–13.

When creating an archive, a conforming producer:

1. **MUST** produce a valid ZIP archive as defined in [Section 4](#4-file-format).
2. **MUST** include a `manifest.json` at the archive root ([Section 6](#6-manifest-file)).
3. **MUST** include `spec.version` in the manifest.
4. **MUST** include `entryPoint` in the manifest, referencing a Markdown file present in the archive. This satisfies rule 1 of the entry point discovery algorithm ([Section 5.5](#55-entry-point-discovery)), so the entry point is unambiguous for every consumer.
5. **SHOULD** include `title` and `mode` in the manifest. When the archive is in project mode, **MUST** set `mode` to `"project"` ([Section 5.7.3](#573-project-mode)).
6. **SHOULD** name the entry point `index.md` at the archive root when the content allows, as the most widely recognized convention.
7. **MUST** use UTF-8 encoding for all Markdown and JSON files.
8. **SHOULD** write LF (`\n`) line endings in Markdown files and `manifest.json` that it creates or modifies, and **SHOULD NOT** change line endings in other files unless the user asks ([Section 12.2](#122-line-endings)).
9. **MUST** use forward-slash path separators in the archive.
10. **MUST NOT** include `..` segments in any entry path ([Section 5.4](#54-path-constraints)).
11. **MUST NOT** include null bytes, ASCII control characters, or OS-reserved characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) in any entry path.
12. **SHOULD** write file paths, and the paths in `entryPoint` and `cover`, in Unicode NFC. **MUST NOT** write two entries whose paths are equal after NFC normalization, empty or `.` segments, or a file whose path is also a directory, and **SHOULD NOT** write two entries whose paths differ only in case ([Section 5.4](#54-path-constraints)). **MUST NOT** write duplicate member names in `manifest.json` ([Section 6.4](#64-manifest-validation)).
13. **MUST NOT** change the capitalization of file names taken from the source content (for example by lowercasing them), unless the user asks. Links are matched case-sensitively ([Section 5.4.1](#541-path-matching)), so renaming a file breaks the links to it.
14. **SHOULD** include all assets referenced by the document's Markdown content.
15. **SHOULD** include `producer.application.name` and `producer.application.version`.
16. When a reusable core library/runtime is part of the producer pipeline, **SHOULD** include `producer.core.name` and `producer.core.version`.
17. **SHOULD** include `producer.application.url`, `producer.core.url`, `author.url`, and `author.email` when available and appropriate to disclose.

A producer that **modifies** an existing archive (for example, adding an `AGENTS.md` or replacing a document) rather than creating one:

1. **MUST NOT** change which file the archive's entry point resolves to, or leave it unresolvable, unless changing the entry point is the purpose of the modification.
2. **SHOULD** add a `manifest.json` with `spec.version` and `entryPoint` when the archive does not have one, using the entry point the archive resolved to before the modification.
3. **MUST** preserve unrecognized manifest fields when rewriting `manifest.json`, as defined in [Section 6.3](#63-additional-fields).
4. **MUST** preserve every archive entry it does not intend to change — including files it does not recognize, cannot render, or does not use, such as `AGENTS.md`, nested support files, unknown file types and files in unfamiliar directories — keeping each entry's path and content byte-for-byte, unless the user explicitly asks for it to be removed. Compression method and ZIP metadata such as timestamps may change.
5. When it cannot display some content of an archive it lets the user edit (an unknown file type, an unsupported Markdown construct), **SHOULD** keep that content and make its presence visible to the user rather than dropping it on save.

Saving an existing archive that has no manifest without adding one is therefore conforming, though not recommended (item 2 above); a creation always writes one.

Conformance is a property of the archive a producer writes, not of the operation alone. A modification **MUST NOT** introduce a violation of [Section 4](#4-file-format), [Section 5.4](#54-path-constraints) or [Section 6](#6-manifest-file). An archive that already violates them (for example, with an entry compressed by an unsupported method, or an invalid name opened through an explicit recovery, [Section 13.1](#131-archive-handling)) stays non-conforming when saved unless the violation is repaired. A producer that saves such an archive **MUST** either repair it with the user's agreement — for example by recompressing the entry with DEFLATE — or tell the user that the saved archive is still non-conforming. It **MUST NOT** repair it silently by dropping or renaming entries ([Section 13.1](#131-archive-handling)).

Archives created by producers targeting earlier versions of this specification, which might not include a manifest, remain valid; consumers handle them as described in [Section 14.2](#142-conforming-consumer).

### 14.2 Conforming Consumer

A conforming consumer is any software that reads and/or processes `.mdz` files. A conforming consumer:

1. **MUST** be able to read the entries of a valid ZIP archive, including entries stored with method 0 or 8 ([Section 4](#4-file-format)). Extracting them to a filesystem is not required; a consumer may read entries directly from the archive.
2. **MUST** determine the primary Markdown file using the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery). When the manifest declares an `entryPoint` that is invalid or not in the archive, **MUST NOT** silently fall back to another file; **SHOULD** report `ERR_ENTRYPOINT_INVALID` or `ERR_ENTRYPOINT_MISSING` respectively, and **MAY** recover using rules 2–4 of Section 5.5 with a visible warning.
3. **MUST NOT** silently select a Markdown file arbitrarily when no unambiguous entry point can be determined. The consumer **SHOULD** present the user with a list of available Markdown files or report a clear error.
4. **MUST** parse `manifest.json` when present, validate it as described in [Section 6.4](#64-manifest-validation), and ignore unrecognized fields. **MUST NOT** require `manifest.json`; an archive without one **MUST** be processed using entry point discovery ([Section 5.5](#55-entry-point-discovery)) and the documented defaults.
5. If `manifest.mode` is present and recognized: when the consumer supports that mode, **MUST** interpret the archive according to it as defined in [Section 5.7](#57-mode-semantics); when it does not (for example, a document-only consumer opening a `project` archive), **MUST** follow [Section 5.7.6](#576-consumer-support-levels) — fail with `ERR_MODE_UNSUPPORTED`, or fall back to `document` mode with a user-visible warning.
6. If `manifest.mode` is present and unrecognized, **MUST NOT** silently fall back to `document` mode. **SHOULD** fail with `ERR_MODE_UNSUPPORTED`.
7. If `manifest.mode` is absent, **MUST** treat the archive as `mode: "document"`.
8. If manifest `cover` is invalid or references a missing file, **SHOULD** ignore `cover` and continue processing the archive; **MAY** emit a warning.
9. **MUST** resolve asset and document links relative to the referencing file's location within the archive, as described in [Section 9.3](#93-path-resolution) (including percent-decoding), matching paths as described in [Section 5.4.1](#541-path-matching) (NFC-normalized, case-sensitive).
10. **MUST** handle entries that violate [Section 5.4](#54-path-constraints), including paths that would escape the archive root, as described in [Section 13.1](#131-archive-handling): never extract them under their stored names, never rename them silently, and never choose between duplicate or conflicting entries.
11. **MUST** treat links outside the archive and links into archives as unresolved unless it supports them; when it does, **MUST** follow [Sections 9.4–9.6](#94-links-outside-the-archive-optional), including treating them as unresolved when the archive has no host filesystem location. **MUST NOT** resolve such a link to a different target, such as a file inside the archive.
12. **MUST** accept text files that use LF (`\n`) or CRLF (`\r\n`) line endings.
13. If `spec.version` is present, **MUST** reject files where the manifest `spec.version` major version exceeds the consumer's supported major version.
14. **MUST** accept both forms of `created` and `modified` (object with required `when`, or a legacy RFC 3339 datetime string), whatever the archive's `spec.version` ([Section 6.1](#61-schema)).

### 14.3 Conformance Fixtures

This repository publishes machine-readable conformance fixtures in [`examples/fixtures/`](examples/fixtures/README.md), and the tests that use them in [`tests/README.md`](tests/README.md). Implementations **SHOULD** run them, pinned to a released tag of this specification.

The fixtures are non-normative. They illustrate the requirements in this document and do not add to them. When a fixture and the prose disagree, the prose governs and the fixture is a defect to report. Passing every fixture does not by itself make an implementation conforming.

---

## 15. Examples

### 15.1 Minimal `.mdz` Archive

A valid minimal `.mdz` archive contains a single Markdown file at the archive root. Naming it `index.md` is the recommended convention. This is the smallest archive a consumer must accept, for example one zipped by hand; an archive written by a conforming producer also includes `manifest.json` ([Section 15.2](#152-document-with-assets)):

**Archive contents:**
```
hello.mdz
└── index.md
```

**`index.md`:**
```markdown
# Hello World

This is a minimal MDZip document.
```

---

### 15.2 Document with Assets

**Archive contents:**
```
my-guide.mdz
├── manifest.json
├── index.md
├── chapter-01.md
└── images/
    ├── cover.png
    └── screenshot.png
```

**`manifest.json`:**
```json
{
  "spec": { "name": "mdzip-spec", "version": "1.2.0" },
  "producer": {
    "application": {
      "name": "mdzip-cli",
      "version": "1.2.0",
      "url": "https://example.com/mdzip-cli"
    },
    "core": {
      "name": "mdzip-core",
      "version": "0.9.4",
      "url": "https://example.com/mdzip-core"
    }
  },
  "author": {
    "name": "Alex Johnson",
    "email": "alex@example.com",
    "url": "https://example.com/~alex"
  },
  "title": "My Guide",
  "mode": "document",
  "entryPoint": "index.md",
  "language": "en",
  "cover": "images/cover.png"
}
```

**`index.md`:**
```markdown
# My Guide

Welcome to the guide. See [Chapter 1](chapter-01.md) to get started.
```

**`chapter-01.md`:**
```markdown
# Chapter 1: Getting Started

Here is a screenshot of the interface:

![Screenshot](images/screenshot.png)
```

---

## 16. Implementation Guidance (Non-Normative)

This section is non-normative and is intended to help tool authors and AI-assisted coding agents implement this specification consistently.

### 16.1 Producer Build Checklist

When creating a `.mdz` archive, a producer can follow this sequence:

1. Collect source Markdown and assets in a staging tree.
2. Normalize text encoding to UTF-8 for Markdown and JSON files.
3. Normalize line endings to LF (`\n`) in Markdown files and `manifest.json`; leave other files as they are ([Section 12.2](#122-line-endings)).
4. Validate file paths against [Section 5.4](#54-path-constraints).
5. Write `manifest.json`:
   - include required fields `spec.version` and `entryPoint`, plus `title` and `mode` (recommended);
   - verify `entryPoint` references a Markdown file in the archive;
   - preserve unknown fields when rewriting an existing manifest ([Section 6.3](#63-additional-fields)), including inside recognized objects.
6. When modifying an existing archive, confirm the entry point still resolves to the same file afterwards ([Section 14.1](#141-conforming-producer)).
7. List any links that point outside the archive ([Section 9.4](#94-links-outside-the-archive-optional)) and report them to the author as an informational notice, since the archive won't be self-contained. Don't rewrite them.
8. Create an unencrypted ZIP archive and use `.mdz` extension.

### 16.2 Consumer Load Checklist

When opening a `.mdz` archive, a consumer can follow this sequence:

1. Open archive as ZIP using the central directory; reject encrypted entries and, optionally, compression methods other than 0 and 8.
2. Enumerate entries and validate them against [Section 5.4](#54-path-constraints): no leading `/`, no empty, `.` or `..` segments, no reserved or control characters, no NFC duplicates, and no file that is also a directory. Reject rather than rename ([Section 13.1](#131-archive-handling)).
3. Parse and validate `manifest.json` if present ([Section 6.4](#64-manifest-validation)): unreadable manifests and invalid critical fields are errors, invalid descriptive fields are ignored, unknown fields are kept. Do not reject the archive if it has no manifest.
4. Check `manifest.mode`: apply a supported mode per [Section 5.7](#57-mode-semantics); default to `document` if absent; for a recognized but unsupported mode, fail or fall back with a visible warning; fail with `ERR_MODE_UNSUPPORTED` if unrecognized.
5. Accept `created` and `modified` in either form (object with required `when`, or legacy RFC 3339 datetime string).
6. If manifest `cover` is invalid or references a missing file, ignore `cover` and optionally warn.
7. Resolve primary Markdown file via [Section 5.5](#55-entry-point-discovery):
   - manifest `entryPoint` is not a valid entry point path: stop with `ERR_ENTRYPOINT_INVALID`, or warn visibly before recovering with rules 2–4;
   - manifest `entryPoint` matches an entry (NFC-normalized, case-sensitive): use it;
   - manifest `entryPoint` matches no entry: stop with `ERR_ENTRYPOINT_MISSING` (optionally naming a case-only near match), or warn visibly before recovering with rules 2–4;
   - no `entryPoint`: apply rules 2–4, setting aside support files (`README`, `AGENTS`, `LICENSE`, `CHANGELOG`, `CONTRIBUTING`) when counting root-level Markdown files.
8. Parse Markdown with UTF-8 decoding and accept LF/CRLF text files.
9. Resolve relative links per [Section 9.3](#93-path-resolution): links that stay inside the archive are internal; links that leave it ([Section 9.4](#94-links-outside-the-archive-optional)) or enter another archive ([Section 9.5](#95-links-into-archives-optional)) are followed only if supported, a host location is known and the target is inside the trust boundary ([Section 9.6](#96-security-and-portability-of-links-beyond-an-archive)), and are otherwise unresolved. Resources loaded automatically from outside the archive stay unresolved unless enabled for the trust boundary. Never clamp `..` at the archive root.
10. If no unambiguous entry point exists, show explicit error or user choice (do not auto-pick arbitrarily).

### 16.3 Terminology Alignment (Producer vs. Create)

Normative specification text uses role terms (`producer`, `consumer`). Implementation APIs and commands may use action-oriented names such as `create` and `add`.

Recommended mapping:

- a `create` API/command is a producer *creation* ([Section 14.1](#141-conforming-producer));
- an `add`, `update` or save API/command on an existing archive is a producer *modification*, which must preserve what it does not change.

### 16.4 Archive Update Semantics (Non-Normative)

When a producer supports adding files to an existing `.mdz` archive:

- path uniqueness should be preserved in the final emitted archive (avoid duplicate logical paths);
- adding a file to an existing path should replace that path's current entry in the resulting archive, rather than retaining duplicate ZIP entries for the same path;
- after successful updates, producers should refresh timestamp metadata (`modified`, and `created` only when creating a new archive);
- when rewriting `manifest.json`, producers preserve unknown fields ([Section 6.3](#63-additional-fields)), and they preserve archive entries they do not change byte-for-byte ([Section 14.1](#141-conforming-producer)). Test both across repeated open/save cycles: a single save that preserves data can hide a second save that drops it.

### 16.5 Suggested Error Categories

Implementations may expose stable error categories to simplify debugging and cross-tool behavior comparisons:

- `ERR_ZIP_INVALID`: archive is not a valid ZIP container, or uses a compression method other than 0 or 8.
- `ERR_ZIP_ENCRYPTED`: archive or entries use unsupported encryption.
- `ERR_PATH_INVALID`: one or more entry paths violate [Section 5.4](#54-path-constraints).
- `ERR_MANIFEST_INVALID`: `manifest.json` is not UTF-8 JSON, its top-level value is not an object, or a critical field has the wrong type or an invalid value ([Section 6.4](#64-manifest-validation)).
- `ERR_ENTRYPOINT_UNRESOLVED`: no unambiguous primary Markdown file can be determined.
- `ERR_ENTRYPOINT_INVALID`: `entryPoint` is not a valid entry point path — not a non-empty string, an unsafe or non-relative path, a directory, or not a `.md`/`.markdown` file ([Section 5.5](#55-entry-point-discovery)).
- `ERR_ENTRYPOINT_MISSING`: `entryPoint` is a valid path but matches no file in the archive, including a match that differs only in case.
- `ERR_VERSION_UNSUPPORTED`: manifest `spec.version` major version is not supported.
- `ERR_PATH_CONFLICT`: a file's path is also the directory of another entry, such as `docs` and `docs/intro.md` ([Section 5.4](#54-path-constraints)).
- `ERR_DUPLICATE_PATH`: duplicate logical archive paths were detected — two entries equal after NFC normalization, or duplicates left by an update operation.
- `ERR_MODE_UNSUPPORTED`: the manifest declares a `mode` value that the consumer does not support or does not recognize.

### 16.6 AI Agent Prompting Tips

To improve deterministic implementation quality, AI prompts should explicitly include:

- the exact target spec version (`1.2.0` or later);
- whether producer, consumer, or both are being implemented;
- required conformance scope (minimum MUSTs vs. SHOULDs included);
- required behavior for ambiguous entry points;
- explicit test expectations from [`tests/README.md`](tests/README.md).

---

## 17. Future Extensions (Non-Normative)

This section records possible future directions and does not define current conformance requirements for `1.2.0`.

### 17.1 Manifest-Level Document Collections

> **Note:** The `document` and `project` mode semantics introduced in [Section 5.7](#57-mode-semantics) address the foundational use case described here. The `documents` array for per-file metadata (title, order, authors) remains a potential future extension and is not defined in this version.

A future version may define an optional manifest field (for example, `documents`) to describe multi-file documents with per-file metadata.

Potential use cases:

- explicit reading/navigation order,
- per-file title/author metadata,
- chapter-level metadata for richer consumers.

One possible shape:

```json
{
  "documents": [
    {
      "path": "chapter-01.md",
      "title": "Introduction",
      "order": 1,
      "authors": ["Jane Smith"]
    }
  ]
}
```

If introduced, future revisions should define:

- interaction with `entryPoint`,
- behavior when listed files are missing or duplicated,
- ordering semantics and tie-breaking rules,
- backward compatibility for consumers that ignore unrecognized fields.

### 17.2 Reader Resume State (Last Read Position)

A future ecosystem convention may define how consumers remember a reader's last opened file and position for an `.mdz` document.

For interoperability and conflict avoidance, this state is best treated as consumer-local user state, not archive content. Implementations should prefer:

- local storage keyed by document identity (for example, path plus content hash),
- per-user state separation,
- non-destructive behavior for read-only archives.

Embedding "last read" data directly inside `.mdz` is not part of this specification and should be avoided unless a future version defines explicit multi-writer and conflict-resolution semantics.

### 17.3 Bookmarks

A future ecosystem convention may define bookmark support so readers can save and return to notable locations within MDZip documents.

As with resume state, bookmark data is best treated as consumer-local user state by default. Implementations should prefer:

- local per-user bookmark storage keyed by document identity,
- bookmark targets that can survive minor content edits where possible,
- non-destructive behavior for read-only archives.

Embedding bookmark data directly inside `.mdz` is not part of this specification and should be avoided unless a future version defines portable bookmark anchoring and conflict-resolution semantics.

### 17.4 Extension Design Principles

Future extensions should:

- preserve portability and minimal baseline interoperability,
- remain optional unless a clear interoperability need requires otherwise,
- avoid coupling the format to any single editor or rendering engine,
- include conformance tests and examples before becoming normative.

### 17.5 Proposal Process

Contributors proposing extensions should open an issue and include:

- problem statement and user impact,
- normative wording draft,
- compatibility analysis,
- proposed conformance tests.

See [CONTRIBUTING.md](CONTRIBUTING.md) for repository workflow.

---

*End of Specification*

