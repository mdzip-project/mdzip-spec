# Markdown Zip (.mdz) File Format Specification

**Version:** 1.0.0-draft  
**Status:** Draft  
**Date:** 2026-03-08

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

---

## 1. Overview

The **Markdown Zip** format (`.mdz`) is a portable, self-contained document format that packages one or more Markdown content files together with their associated assets—such as images, stylesheets, and other referenced resources—into a single ZIP archive.

A `.mdz` file allows authors to distribute complete Markdown-based documents without broken asset references, and enables readers and tools to reliably open and render the document without external dependencies.

This specification follows established standards patterns by using RFC 2119 normative language, Semantic Versioning, and UTF-8/JSON conventions compatible with other open document and text-based standards (such as CommonMark, EPUB, and TOML ecosystems).

---

## 2. Goals and Non-Goals

### Goals

- Provide a simple, open, and inspectable container format for Markdown documents.
- Ensure documents and all referenced assets travel together as a single unit.
- Support multiple Markdown pages/sections within a single archive.
- Be renderable by any tool that understands ZIP extraction and standard Markdown.
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
| **Manifest** | The optional `manifest.json` file at the root of the archive describing document metadata and entry-point overrides. |
| **Asset** | Any non-Markdown file referenced by a Markdown content file (e.g., images, stylesheets). |
| **Conforming producer** | Software that creates `.mdz` files according to this specification. |
| **Conforming consumer** | Software that reads and renders `.mdz` files according to this specification. |

---

## 4. File Format

A `.mdz` file is a **ZIP archive** as defined by the [ZIP Application Note (APPNOTE.TXT)](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT) version 6.3.10 or later.

Requirements:

- The archive **MUST** be a valid ZIP file.
- The archive **MUST NOT** use ZIP64 extensions unless the content requires it (i.e., individual files or archive exceeds 4 GB).
- Files inside the archive **MUST** use UTF-8 encoded file paths.
- File path separators inside the archive **MUST** be forward slashes (`/`).
- The archive **MAY** use DEFLATE compression (method 8) or store without compression (method 0) for individual entries.
- The archive **MUST NOT** use password protection or encryption.
- Conforming producers **SHOULD** write LF (`\n`) line endings for all text files within the archive (including Markdown, JSON, and plain-text assets).
- Conforming consumers **MUST** accept text files that use LF (`\n`) or CRLF (`\r\n`) line endings.
- Conforming producers **SHOULD** normalize line endings to LF when writing `.mdz` files, even if source content originated from platforms that use other line-ending conventions.

---

## 5. Archive Structure

A `.mdz` file is a ZIP archive containing at least one Markdown file that can be resolved as the primary document using the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery). A `manifest.json` file at the archive root is OPTIONAL. All other files are organized relative to the archive root.

### 5.1 Required Files

There are no unconditionally required files beyond the archive being a valid ZIP. However, the archive **MUST** contain at least one Markdown file that satisfies the entry point discovery rules in [Section 5.5](#55-entry-point-discovery).

### 5.2 Optional Files

| Path | Description |
|------|-------------|
| `index.md` | Conventional entry point Markdown file (see [Section 5.5](#55-entry-point-discovery)). |
| `manifest.json` | Optional document manifest (see [Section 6](#6-manifest-file)). |
| `README.md` | Optional human-facing guidance for environments without full `.mdz` tooling. |

### 5.3 Recommended Layout

```
document.mdz (ZIP archive)
├── index.md               # Recommended: conventional entry point
├── manifest.json          # Optional: metadata and entry-point override
├── README.md              # Optional: human-facing usage notes
├── chapter-01.md          # Additional Markdown files (optional)
├── chapter-02.md
└── assets/                # Recommended directory for non-Markdown files
    ├── images/
    │   ├── cover.png
    │   └── diagram.svg
    └── styles/
        └── style.css
```

### 5.4 Path Constraints

- All file paths inside the archive **MUST** be relative to the archive root.
- File paths **MUST NOT** begin with a leading slash (`/`).
- File paths **MUST NOT** contain path traversal sequences (e.g., `../`).
- File paths **MUST NOT** contain null bytes or ASCII control characters (U+0000–U+001F, U+007F).
- File paths **MUST NOT** contain characters reserved by common operating systems: `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`.
- File paths **SHOULD** use lowercase characters.

### 5.5 Entry Point Discovery

Conforming consumers **MUST** determine the primary Markdown file using the following ordered algorithm:

1. If `manifest.json` is present at the archive root and contains a valid `entryPoint` value referencing an existing file in the archive, use that file.
2. If `index.md` exists at the archive root, use it.
3. If exactly one `.md` or `.markdown` file exists at the archive root, use it.
4. Otherwise, the consumer **MUST NOT** silently select a file arbitrarily. The consumer **SHOULD** present the user with a list of available Markdown files to choose from, or report a clear error indicating that no unambiguous entry point could be determined.

Conforming producers **SHOULD** ensure their archives satisfy one of the first three conditions to guarantee unambiguous entry point resolution across all consumers. Including `index.md` at the archive root or providing a `manifest.json` with `entryPoint` defined are the most interoperable approaches.

### 5.6 Human-Facing `README.md` (Optional)

Producers **SHOULD** include a root-level `README.md` when practical, especially for files likely to be opened by recipients without `.mdz`-aware tooling.

Because `README.md` is inside the archive, producers distributing `.mdz` to likely unaware recipients **SHOULD** provide a primary discovery method outside the archive. Examples include:

- a download-page note describing `.mdz` and basic opening steps,
- a companion sidecar text file next to the `.mdz` file,
- a website/help link shown wherever the file is shared.

When present, `README.md` **SHOULD** briefly include:

- what the archive is (`.mdz` / Markdown Zip),
- where primary document content begins (for example, `index.md`),
- how to open the package with standard tools (for example, unzip then open Markdown files),
- where to find format documentation (for example, a project URL).

Producers **MAY** include instructions for opening the package with a specific consumer tool. When they do, they **SHOULD** also include a generic fallback workflow (for example, unzip and open `index.md`) so the package remains understandable without that specific tool.

`README.md` is a secondary aid and does not replace out-of-archive discovery guidance for unaware recipients. It is informational only and does not affect entry point discovery or conformance logic.

---

## 6. Manifest File

The manifest file, when present, **MUST** be named `manifest.json` and placed at the root of the archive. It **MUST** be a valid [JSON](https://www.rfc-editor.org/rfc/rfc8259) document encoded in UTF-8.

Producer tools **MAY** accept non-JSON authoring inputs (for example, JSON5) as a local convenience, but conforming `.mdz` archives **MUST** contain `manifest.json` serialized as standard JSON per RFC 8259.

### 6.1 Schema

```json
{
  "mdz": "<spec version>",
  "title": "<document title>",
  "entryPoint": "<path to entry point markdown file>",
  "language": "<BCP 47 language tag>",
  "authors": [
    {
      "name": "<author name>",
      "email": "<author email>"
    }
  ],
  "description": "<short description>",
  "version": "<document version>",
  "created": "<ISO 8601 datetime>",
  "modified": "<ISO 8601 datetime>",
  "license": "<SPDX license identifier or URL>",
  "keywords": ["<keyword>"],
  "cover": "<path to cover image asset>"
}
```

> **Required fields** (when manifest is present): `mdz`, `title`. All other fields are OPTIONAL.

### 6.2 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mdz` | string | **REQUIRED (if manifest is present)** | The version of this specification the file conforms to. **MUST** be a [Semantic Versioning 2.0.0](https://semver.org/) string (e.g., `"1.0.0"`). |
| `title` | string | **REQUIRED (if manifest is present)** | The human-readable title of the document. **MUST NOT** be empty. |
| `entryPoint` | string | OPTIONAL | Path to the primary Markdown file, relative to the archive root (e.g., `"chapters/start.md"`). The referenced file **MUST** exist in the archive. If omitted, consumers apply the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery). |
| `language` | string | OPTIONAL | The natural language of the document as a [BCP 47](https://www.rfc-editor.org/rfc/rfc5646) language tag (e.g., `"en"`, `"fr-CA"`). Defaults to `"en"` if omitted. |
| `authors` | array | OPTIONAL | An array of author objects. Each object **MAY** include `name` (string) and `email` (string) fields. |
| `description` | string | OPTIONAL | A short plain-text description of the document. |
| `version` | string | OPTIONAL | The version of the document itself (not the spec version). **SHOULD** follow Semantic Versioning. |
| `created` | string | OPTIONAL | The creation datetime of the document in [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) format (e.g., `"2026-03-08T12:00:00Z"`). |
| `modified` | string | OPTIONAL | The last-modified datetime of the document in ISO 8601 format. |
| `license` | string | OPTIONAL | An [SPDX license identifier](https://spdx.org/licenses/) (e.g., `"MIT"`, `"CC-BY-4.0"`) or a URL pointing to the license text. |
| `keywords` | array of strings | OPTIONAL | A list of keywords or tags describing the document. |
| `cover` | string | OPTIONAL | Archive-root-relative path to a cover image asset (e.g., `"assets/images/cover.png"`). The referenced file **MUST** exist in the archive if specified. |

### 6.3 Additional Fields

Conforming producers **MAY** include additional fields not defined in this specification. Conforming consumers **MUST** ignore any unrecognized fields.

### 6.4 Example Manifest

```json
{
  "mdz": "1.0.0",
  "title": "My Technical Guide",
  "entryPoint": "index.md",
  "language": "en",
  "authors": [
    {
      "name": "Jane Smith",
      "email": "jane@example.com"
    }
  ],
  "description": "A comprehensive guide to building widgets.",
  "version": "2.1.0",
  "created": "2026-01-15T09:00:00Z",
  "modified": "2026-03-08T14:30:00Z",
  "license": "CC-BY-4.0",
  "keywords": ["widgets", "guide", "tutorial"],
  "cover": "assets/images/cover.png"
}
```

---

## 7. Markdown Content Files

### 7.1 Encoding

All Markdown files inside the archive **MUST** be encoded in UTF-8.

### 7.2 Markdown Dialect

This specification does not mandate a specific Markdown dialect. Producers **SHOULD** note in the manifest `description` or within the document itself which dialect is used (e.g., [CommonMark](https://commonmark.org/), [GitHub Flavored Markdown](https://github.github.com/gfm/)).

### 7.3 File Extensions

Markdown files **SHOULD** use the `.md` file extension. The `.markdown` extension is also permitted.

### 7.4 Multiple Pages

A `.mdz` archive **MAY** contain multiple Markdown files, allowing a document to be split across chapters, sections, or pages. The primary document is `index.md` by default, or the file identified by `entryPoint` when a manifest is present and specifies it. Other Markdown files **SHOULD** be linked from the primary document or from other Markdown files within the archive using relative paths.

---

## 8. Asset Files

Asset files are any non-Markdown files bundled in the archive, such as images, stylesheets, fonts, or data files.

### 8.1 Placement

Assets **SHOULD** be placed under an `assets/` directory at the archive root. Subdirectories within `assets/` are permitted and **RECOMMENDED** for organization (e.g., `assets/images/`, `assets/styles/`).

### 8.2 Allowed Asset Types

There is no restriction on asset file types. However, producers **SHOULD** only include assets that are directly referenced by the document's Markdown content.

### 8.3 Unused Assets

Conforming producers **SHOULD NOT** include asset files that are not referenced by any Markdown file in the archive.

---

## 9. Linking and References

### 9.1 Internal Links

References to other files within the archive (Markdown files and assets) **MUST** use **relative paths** based on the location of the referencing file within the archive.

**Example:** A Markdown file at the archive root (`index.md`) referencing an image:
```markdown
![Diagram](assets/images/diagram.svg)
```

**Example:** A Markdown file in a subdirectory (`chapters/intro.md`) referencing an image at the archive root:
```markdown
![Logo](../assets/images/logo.png)
```

### 9.2 External Links

Links to external URLs (e.g., `https://example.com`) are permitted. Conforming consumers **MAY** choose to warn users before following external links.

### 9.3 Path Resolution

Conforming consumers **MUST** resolve relative paths against the path of the referencing file within the archive. Consumers **MUST** reject or ignore any path that resolves outside the archive root (i.e., any path traversal attempt).

---

## 10. MIME Type and File Extension

| Property | Value |
|----------|-------|
| **File extension** | `.mdz` |
| **MIME type** | `application/vnd.markdownzip` |

Producers and consumers **SHOULD** use the `.mdz` file extension. The MIME type `application/vnd.markdownzip` **SHOULD** be used when the format is transmitted over HTTP or identified in metadata.

`application/vnd.markdownzip` is currently an unregistered vendor media type in this draft. Until formal registration is completed, implementations **MAY** treat it as provisional for interoperability testing.

---

## 11. Versioning

### 11.1 Specification Versioning

This specification uses [Semantic Versioning 2.0.0](https://semver.org/):

- **Major version** increments indicate breaking, backwards-incompatible changes to the format.
- **Minor version** increments indicate backwards-compatible additions or clarifications.
- **Patch version** increments indicate corrections or editorial changes with no impact on format compatibility.

### 11.2 Manifest `mdz` Field

When `manifest.json` is present, the `mdz` field identifies the version of this specification that the producing tool targeted. Conforming consumers:

- **MUST** reject files where the `mdz` field major version is higher than the highest major version the consumer supports.
- **SHOULD** warn users when the `mdz` field major version is lower than the consumer's current major version support.
- **MUST** accept files where the `mdz` field minor or patch version differs from the consumer's supported version, provided the major version matches.

### 11.3 Files Without `manifest.json`

When `manifest.json` is omitted, the archive is unversioned. Conforming consumers:

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

- Conforming producers **SHOULD** normalize text files to LF (`\n`) line endings when writing `.mdz`.
- Conforming consumers **MUST** accept text files using LF (`\n`) and CRLF (`\r\n`) line endings.

### 12.3 Path and Case Behavior

- Paths inside archives **MUST** use forward slashes (`/`), regardless of host platform.
- Consumers **SHOULD** treat archive paths as case-sensitive for deterministic behavior across operating systems.
- Unknown manifest fields **MUST** be ignored to preserve forward compatibility.

### 12.4 Markdown Dialect Portability

- Producers **SHOULD** prefer portable Markdown constructs that degrade gracefully in CommonMark-class renderers.
- Producers **SHOULD** document non-portable syntax expectations when relying on dialect-specific features.

---

## 13. Security Considerations

Conforming consumers and producers should treat `.mdz` content as potentially untrusted input. The following controls are recommended to reduce risk.

### 13.1 Archive Handling

- Consumers **MUST** reject path traversal attempts that resolve outside archive root (e.g., `../`, absolute paths).
- Consumers **MUST** reject or sanitize archive entries whose paths contain characters prohibited by Section 5.4 (null bytes, control characters, or OS-reserved characters) before writing to the local filesystem.
- Consumers **SHOULD** enforce limits on extracted entry count, total uncompressed bytes, and compression ratio to mitigate ZIP bomb attacks.
- Consumers **SHOULD** ignore or safely handle symbolic links and hard links if exposed by the ZIP library.

### 13.2 Content Handling

- Consumers **MUST NOT** execute scripts or binaries from `.mdz` content as part of normal rendering.
- Consumers **SHOULD** warn before opening external URLs found in document links.
- Consumers **SHOULD** apply implementation-specific size/time limits while parsing large Markdown or metadata files.

### 13.3 Producer Guidance

- Producers **SHOULD NOT** include credentials, private keys, or other secrets in archive content.
- Producers **SHOULD** include only assets required for rendering the document.

---

## 14. Conformance

### 14.1 Conforming Producer

A conforming producer is any software that creates `.mdz` files. A conforming producer:

1. **MUST** produce a valid ZIP archive as defined in [Section 4](#4-file-format).
2. **MUST** ensure the archive satisfies at least one of the first three conditions of the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery).
3. **SHOULD** include `index.md` at the archive root or provide a `manifest.json` with `entryPoint` defined, as these are the most broadly compatible approaches.
4. **MUST** include the file referenced by `entryPoint` when a manifest is present and defines `entryPoint`.
5. **MUST** use UTF-8 encoding for all Markdown and JSON files.
6. **SHOULD** write LF (`\n`) line endings for all text files in the archive.
7. **MUST** use forward-slash path separators in the archive.
8. **MUST NOT** include path traversal sequences in any file path.
9. **MUST NOT** include null bytes, ASCII control characters, or OS-reserved characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) in any file path.
10. **SHOULD** include all assets referenced by the document's Markdown content.

### 14.2 Conforming Consumer

A conforming consumer is any software that reads and/or renders `.mdz` files. A conforming consumer:

1. **MUST** be able to open and extract a valid ZIP archive.
2. **MUST** determine the primary Markdown file using the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery).
3. **MUST NOT** silently select a Markdown file arbitrarily when no unambiguous entry point can be determined. The consumer **SHOULD** present the user with a list of available Markdown files or report a clear error.
4. **MUST** parse `manifest.json` when present and ignore unrecognized fields.
5. **MUST** resolve asset and document links relative to the referencing file's location within the archive.
6. **MUST** reject or safely handle any path that traverses outside the archive root.
7. **MUST** accept text files that use LF (`\n`) or CRLF (`\r\n`) line endings.
8. **MUST** reject files where the manifest `mdz` major version exceeds the consumer's supported major version, when a manifest is present.

---

## 15. Examples

### 15.1 Minimal `.mdz` Archive

A valid minimal `.mdz` archive contains a single Markdown file at the archive root. Naming it `index.md` is the recommended convention:

**Archive contents:**
```
hello.mdz
└── index.md
```

**`index.md`:**
```markdown
# Hello World

This is a minimal Markdown Zip document.
```

---

### 15.2 Document with Assets

**Archive contents:**
```
my-guide.mdz
├── manifest.json
├── index.md
├── chapter-01.md
└── assets/
    └── images/
        ├── cover.png
        └── screenshot.png
```

**`manifest.json`:**
```json
{
  "mdz": "1.0.0",
  "title": "My Guide",
  "entryPoint": "index.md",
  "language": "en",
  "authors": [{ "name": "Alex Johnson" }],
  "cover": "assets/images/cover.png"
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

![Screenshot](assets/images/screenshot.png)
```

---

## 16. Implementation Guidance (Non-Normative)

This section is non-normative and is intended to help tool authors and AI-assisted coding agents implement this specification consistently.

### 16.1 Producer Build Checklist

When creating a `.mdz` archive, a producer can follow this sequence:

1. Collect source Markdown and assets in a staging tree.
2. Normalize text encoding to UTF-8 for Markdown and JSON files.
3. Normalize text line endings to LF (`\n`) where practical.
4. Validate file paths against [Section 5.4](#54-path-constraints).
5. If `manifest.json` is present:
   - verify required manifest fields (`mdz`, `title`);
   - verify `entryPoint`, if present, exists in the archive;
   - preserve unknown fields as-is when round-tripping.
6. Ensure at least one unambiguous entry point condition from [Section 5.5](#55-entry-point-discovery) is satisfied.
7. Create an unencrypted ZIP archive and use `.mdz` extension.

### 16.2 Consumer Load Checklist

When opening a `.mdz` archive, a consumer can follow this sequence:

1. Open archive as ZIP and reject encrypted/password-protected entries.
2. Enumerate entries and validate path safety constraints ([Section 5.4](#54-path-constraints)).
3. Parse `manifest.json` if present, ignoring unknown fields.
4. Resolve primary Markdown file via [Section 5.5](#55-entry-point-discovery).
5. Parse Markdown with UTF-8 decoding and accept LF/CRLF text files.
6. Resolve relative links per [Section 9](#9-linking-and-references), rejecting escape attempts outside archive root.
7. If no unambiguous entry point exists, show explicit error or user choice (do not auto-pick arbitrarily).

### 16.3 Suggested Error Categories

Implementations may expose stable error categories to simplify debugging and cross-tool behavior comparisons:

- `ERR_ZIP_INVALID`: archive is not a valid ZIP container.
- `ERR_ZIP_ENCRYPTED`: archive or entries use unsupported encryption.
- `ERR_PATH_INVALID`: one or more entry paths violate [Section 5.4](#54-path-constraints).
- `ERR_MANIFEST_INVALID`: `manifest.json` is malformed or missing required fields when present.
- `ERR_ENTRYPOINT_UNRESOLVED`: no unambiguous primary Markdown file can be determined.
- `ERR_ENTRYPOINT_MISSING`: `entryPoint` references a file not present in archive.
- `ERR_VERSION_UNSUPPORTED`: manifest `mdz` major version is not supported.

### 16.4 AI Agent Prompting Tips

To improve deterministic implementation quality, AI prompts should explicitly include:

- the exact target spec version (`1.0.0-draft` or later);
- whether producer, consumer, or both are being implemented;
- required conformance scope (minimum MUSTs vs. SHOULDs included);
- required behavior for ambiguous entry points;
- explicit test expectations from [`tests/README.md`](tests/README.md).

---

*End of Specification*
