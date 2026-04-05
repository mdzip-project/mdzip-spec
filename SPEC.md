# MDZip (.mdz) File Format Specification

**Version:** 1.1.0-draft  
**Status:** Draft  
**Date:** 2026-04-05

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

The **MDZip** format (`.mdz`) is a portable, self-contained document format that packages one or more Markdown content files together with their associated assets—such as images, stylesheets, and other referenced resources—into a single ZIP archive.

An `.mdz` file allows authors to distribute complete Markdown-based documents without broken asset references, and enables readers and tools to reliably open and render the document without external dependencies.

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
| **Conforming consumer** | Software that reads and/or processes `.mdz` files according to this specification. |
| **Mode** | The declared interpretation intent of an archive's contents, specified via `manifest.mode`. Controls how consumers render and navigate content. |
| **Document mode** | A mode in which the archive represents a single logical document. The default when no mode is declared. |
| **Project mode** | A mode in which the archive represents a collection of independent Markdown documents. Requires an explicit manifest declaring `"mode": "project"`. |

---

## 4. File Format

An `.mdz` file is a **ZIP archive** as defined by the [ZIP Application Note (APPNOTE.TXT)](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT) version 6.3.10 or later.

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

An `.mdz` file is a ZIP archive containing at least one Markdown file that can be resolved as the primary document using the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery). A `manifest.json` file at the archive root is OPTIONAL. All other files are organized relative to the archive root.

### 5.1 Required Files

There are no unconditionally required files beyond the archive being a valid ZIP. However, the archive **MUST** contain at least one Markdown file that satisfies the entry point discovery rules in [Section 5.5](#55-entry-point-discovery).

### 5.2 Optional Files

| Path | Description |
|------|-------------|
| `index.md` | Conventional entry point Markdown file (see [Section 5.5](#55-entry-point-discovery)). |
| `manifest.json` | Optional document manifest (see [Section 6](#6-manifest-file)). |
| `README.md` | Optional human-facing guidance for environments without full `.mdz` tooling. |

### 5.3 Recommended Layout

#### Document Mode

```
document.mdz (ZIP archive)
├── index.md               # Recommended: conventional entry point
├── manifest.json          # Optional: metadata and entry-point override
├── README.md              # Optional: human-facing usage notes
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

- All file paths inside the archive **MUST** be relative to the archive root.
- File paths **MUST NOT** begin with a leading slash (`/`).
- File paths **MUST NOT** contain path traversal sequences (e.g., `../`).
- File paths **MUST NOT** contain null bytes or ASCII control characters (U+0000–U+001F, U+007F).
- File paths **MUST NOT** contain characters reserved by common operating systems: `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`.
- File paths **SHOULD** use lowercase characters.

See [Section 13.1](#131-archive-handling) for consumer requirements on rejecting non-conforming paths.

### 5.5 Entry Point Discovery

Conforming consumers **MUST** determine the primary Markdown file using the following ordered algorithm:

1. If `manifest.json` is present at the archive root and contains a valid `entryPoint` value referencing an existing file in the archive, use that file.
2. If `index.md` exists at the archive root, use it.
3. If exactly one `.md` or `.markdown` file exists at the archive root, use it.
4. Otherwise, the consumer **MUST NOT** silently select a file arbitrarily. The consumer **SHOULD** present the user with a list of available Markdown files to choose from, or report a clear error indicating that no unambiguous entry point could be determined.

Conforming producers **MUST** ensure their archives satisfy at least one of the first three conditions to guarantee unambiguous entry point resolution across all consumers. Including `index.md` at the archive root or providing a `manifest.json` with `entryPoint` defined are the most interoperable approaches.

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

`README.md` is a secondary aid and does not replace out-of-archive discovery guidance for unaware recipients. It is informational only and does not affect entry point discovery or conformance logic.

A reusable sample is available at [`examples/templates/README.sample.md`](examples/templates/README.sample.md).

### 5.7 Mode Semantics

An `.mdz` archive has an **interpretation mode** that tells conforming consumers how to render and navigate its contents. Mode is either applied by default or explicitly declared via `manifest.mode`. Mode values are case-sensitive and MUST be lowercase.

#### 5.7.1 Mode Defaults

If `manifest.json` is absent, or if `manifest.json` is present but does not include a `mode` field, consumers MUST treat the archive as `mode: "document"`. This is a default, not an inference — the rule is deterministic and requires no examination of archive contents.

The number of Markdown files present, their names, or the directory structure of the archive MUST NOT influence mode selection.

#### 5.7.2 Document Mode

`document` mode indicates that the archive represents a **single logical document**, regardless of how many Markdown files it contains.

**Consumers MUST:**

- Resolve the entry point using the standard entry point discovery algorithm (Section 5.5)
- Render content as a single document

**Consumers MAY:**

- Inline or process referenced Markdown files as part of a unified document view
- Apply transformations that produce a single rendered output

This is the default mode and applies when no manifest is present or when `manifest.mode` is `"document"`.

#### 5.7.3 Project Mode

`project` mode indicates that the archive represents a **collection of independent Markdown documents** with navigational relationships between them.

**Requirements:**

- A `manifest.json` file MUST be present
- The manifest MUST declare `"mode": "project"`
- The manifest SHOULD define a valid `entryPoint`

**Consumers MUST:**

- Treat each Markdown file as a separate document
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

- If `manifest.entryPoint` is present, it MUST be used as the primary entry point
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

A consumer MUST NOT silently render an archive incorrectly when it encounters a mode it cannot handle. For **unrecognized** mode values (values not defined in this spec), consumers MUST NOT fall back silently and SHOULD fail with `ERR_MODE_UNSUPPORTED`. For **recognized but unsupported** modes (e.g. a document-only consumer encountering `project`), warn-and-fallback to `document` is conforming provided the warning is user-visible.

---

## 6. Manifest File

The manifest file, when present, **MUST** be named `manifest.json` and placed at the root of the archive. It **MUST** be a valid [JSON](https://www.rfc-editor.org/rfc/rfc8259) document encoded in UTF-8.

Producer tools **MAY** accept non-JSON authoring inputs (for example, JSON5) as a local convenience, but conforming `.mdz` archives **MUST** contain `manifest.json` serialized as standard JSON per RFC 8259.

A versioned JSON Schema companion for this draft is available at [`schema/manifest-1.1.0-draft.schema.json`](schema/manifest-1.1.0-draft.schema.json). The prose specification remains normative when differences exist.

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
    "when": "<ISO 8601 datetime>",
    "by": {
      "name": "<creator name>",
      "email": "<creator email>",
      "url": "<creator URL>"
    }
  },
  "modified": {
    "when": "<ISO 8601 datetime>",
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

During draft `1.0.x`, `created` and `modified` MAY each be either:

- a string ISO 8601 datetime (legacy draft form), or
- an object with required `when` and optional `by`.

> **Required fields:** none for arbitrary hand-authored manifests.  
> For **conforming producer-generated** manifests, `spec.version` is REQUIRED.

### 6.2 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `spec` | object | OPTIONAL | Container for spec compatibility metadata. |
| `spec.name` | string | OPTIONAL | Identifier for the target specification (e.g., `"mdzip-spec"`). |
| `spec.version` | string | CONDITIONALLY REQUIRED | The version of this specification the file conforms to. **MUST** be a [Semantic Versioning 2.0.0](https://semver.org/) string (e.g., `"1.1.0"`). **REQUIRED** when `manifest.json` is emitted by a conforming producer. |
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
| `title` | string | OPTIONAL | The human-readable title of the document. If present, it **MUST NOT** be empty. If omitted, consumers **SHOULD** derive a display title from available context (for example, the entry-point, filename or first heading). |
| `mode` | string | OPTIONAL | The interpretation mode of the archive. Allowed values: `"document"` (default), `"project"`. Values are case-sensitive and MUST be lowercase. If absent, consumers MUST assume `"document"`. If present with an unrecognized value (including incorrect casing such as `"Document"` or `"PROJECT"`), consumers MUST NOT silently fall back to `document` mode. MUST be `"project"` when the archive represents a multi-document structure. See [Section 5.7](#57-mode-semantics). |
| `entryPoint` | string | OPTIONAL | Path to the primary Markdown file, relative to the archive root (e.g., `"chapters/start.md"`). The referenced file **MUST** exist in the archive. If omitted, consumers apply the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery). |
| `language` | string | OPTIONAL | The natural language of the document as a [BCP 47](https://www.rfc-editor.org/rfc/rfc5646) language tag (e.g., `"en"`, `"fr-CA"`). Defaults to `"en"` if omitted. |
| `description` | string | OPTIONAL | A short plain-text description of the document. |
| `version` | string | OPTIONAL | The version of the document itself (not the spec version). **SHOULD** follow Semantic Versioning. |
| `created` | string or object | OPTIONAL | Creation metadata. During draft `1.0.x`, consumers **MUST** accept both forms: ISO 8601 string (legacy) and object form. |
| `created.when` | string | CONDITIONALLY REQUIRED | Required when `created` is an object. The creation datetime in ISO 8601 format. |
| `created.by` | object | OPTIONAL | Creator identity metadata when known and appropriate to disclose. |
| `created.by.name` | string | OPTIONAL | Creator display name. |
| `created.by.email` | string | OPTIONAL | Creator contact address. |
| `created.by.url` | string | OPTIONAL | Creator website/profile URL. |
| `modified` | string or object | OPTIONAL | Last-modified metadata. During draft `1.0.x`, consumers **MUST** accept both forms: ISO 8601 string (legacy) and object form. |
| `modified.when` | string | CONDITIONALLY REQUIRED | Required when `modified` is an object. The last-modified datetime in ISO 8601 format. |
| `modified.by` | object | OPTIONAL | Modifier identity metadata when known and appropriate to disclose. |
| `modified.by.name` | string | OPTIONAL | Modifier display name. |
| `modified.by.email` | string | OPTIONAL | Modifier contact address. |
| `modified.by.url` | string | OPTIONAL | Modifier website/profile URL. |
| `license` | string | OPTIONAL | An [SPDX license identifier](https://spdx.org/licenses/) (e.g., `"MIT"`, `"CC-BY-4.0"`) or a URL pointing to the license text. |
| `keywords` | array of strings | OPTIONAL | A list of keywords or tags describing the document. |
| `cover` | string | OPTIONAL | Archive-root-relative path to a cover image asset (e.g., `"images/cover.png"`). If present, it **MUST** reference an existing file in the archive. If `cover` is present but the referenced file is missing, conforming consumers **SHOULD** ignore `cover` and continue processing the archive; they **MAY** emit a warning. |

### 6.3 Additional Fields

Conforming producers **MAY** include additional fields not defined in this specification. Conforming consumers **MUST** ignore any unrecognized fields.

### 6.4 Example Manifests

#### Document Mode (default — `mode` field may be omitted)

```json
{
  "spec": {
    "name": "mdzip-spec",
    "version": "1.1.0"
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
    "version": "1.1.0"
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

Markdown files **SHOULD** use the `.md` file extension. The `.markdown` extension is also permitted.

### 7.4 Multiple Pages

An `.mdz` archive **MAY** contain multiple Markdown files, allowing a document to be split across chapters, sections, or pages. The primary document is `index.md` by default, or the file identified by `entryPoint` when a manifest is present and specifies it. Other Markdown files **SHOULD** be linked from the primary document or from other Markdown files within the archive using relative paths.

---

## 8. Asset Files

Asset files are any non-Markdown files bundled in the archive, such as images, stylesheets, fonts, or data files.

### 8.1 Placement

Assets **SHOULD** be organized in named subdirectories at the archive root, grouped by type (e.g., `images/`, `styles/`, `fonts/`, `pdf/`). Additional hierarchy within those directories is **RECOMMENDED** when the volume of files warrants it. A dedicated `assets/` parent directory **MAY** be used to group all asset directories together, but is not required.

### 8.2 Allowed Asset Types

There is no restriction on asset file types. However, producers **SHOULD** only include assets that are directly referenced by the document's Markdown content.

### 8.3 Unused Assets

Conforming producers **SHOULD NOT** include asset files that are not referenced by any Markdown file in the archive.

---

## 9. Linking and References

### 9.1 Internal Links

References to other files within the archive (Markdown files and assets) **MUST** use **relative paths** based on the location of the referencing file within the archive.
Relative links **MAY** include `../` segments as long as the resolved path remains within the archive root.

**Example:** A Markdown file at the archive root (`index.md`) referencing an image:
```markdown
![Diagram](images/diagram.svg)
```

**Example:** A Markdown file in a subdirectory (`chapters/intro.md`) referencing an image at the archive root:
```markdown
![Logo](../images/logo.png)
```

### 9.2 External Links

Links to external URLs (e.g., `https://example.com`) are permitted. Conforming consumers **MAY** choose to warn users before following external links.

### 9.3 Path Resolution

Conforming consumers **MUST** resolve relative paths against the path of the referencing file within the archive. Consumers **MUST** reject or ignore any path that resolves outside the archive root after normalization (i.e., any path traversal attempt).

---

## 10. MIME Type and File Extension

| Property | Value |
|----------|-------|
| **File extension** | `.mdz` |
| **MIME type** | Proposed `application/vnd.mdzip` |

Producers and consumers **SHOULD** use the `.mdz` file extension. The proposed MIME type `application/vnd.mdzip` **SHOULD** be used when the format is transmitted over HTTP or identified in metadata.

`application/vnd.mdzip` is currently an unregistered vendor media type in this draft. Until formal registration is completed, implementations **MAY** treat it as provisional for interoperability testing. For broad interoperability, servers **MAY** use `application/zip` or `application/octet-stream` as a fallback until `application/vnd.mdzip` is more widely recognized.

---

## 11. Versioning

### 11.1 Specification Versioning

This specification uses [Semantic Versioning 2.0.0](https://semver.org/):

- **Major version** increments indicate breaking, backwards-incompatible changes to the format.
- **Minor version** increments indicate backwards-compatible additions or clarifications.
- **Patch version** increments indicate corrections or editorial changes with no impact on format compatibility.

### 11.2 Manifest `spec.version` Field

When `manifest.json` includes `spec.version`, it identifies the version of this specification that the producing tool targeted. Conforming consumers:

- **MUST** reject files where `spec.version` major version is higher than the highest major version the consumer supports.
- **SHOULD** warn users when `spec.version` major version is lower than the consumer's current major version support.
- **MUST** accept files where `spec.version` minor or patch version differs from the consumer's supported version, provided the major version matches.

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

- Consumers **MUST** reject path traversal attempts that resolve outside archive root after normalization (e.g., absolute paths or relative paths that escape the root).
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
5. When `manifest.mode` is `"project"`, **MUST** ensure the archive satisfies at least one of the first three conditions of the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery). **SHOULD** include `entryPoint` explicitly as the most interoperable approach.
6. **MUST** use UTF-8 encoding for all Markdown and JSON files.
7. **SHOULD** write LF (`\n`) line endings for all text files in the archive.
8. **MUST** use forward-slash path separators in the archive.
9. **MUST NOT** include path traversal sequences in any file path.
10. **MUST NOT** include null bytes, ASCII control characters, or OS-reserved characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) in any file path.
11. **SHOULD** include all assets referenced by the document's Markdown content.
12. When a manifest is emitted, **MUST** include `spec.version`.
13. **SHOULD** include `producer.application.name` and `producer.application.version`.
14. When a reusable core library/runtime is part of the producer pipeline, **SHOULD** include `producer.core.name` and `producer.core.version`.
15. **SHOULD** include `producer.application.url`, `producer.core.url`, `author.url`, and `author.email` when available and appropriate to disclose.

### 14.2 Conforming Consumer

A conforming consumer is any software that reads and/or processes `.mdz` files. A conforming consumer:

1. **MUST** be able to open and extract a valid ZIP archive.
2. **MUST** determine the primary Markdown file using the entry point discovery algorithm defined in [Section 5.5](#55-entry-point-discovery).
3. **MUST NOT** silently select a Markdown file arbitrarily when no unambiguous entry point can be determined. The consumer **SHOULD** present the user with a list of available Markdown files or report a clear error.
4. **MUST** parse `manifest.json` when present and ignore unrecognized fields.
5. If `manifest.mode` is present and recognized, **MUST** interpret the archive according to the declared mode as defined in [Section 5.7](#57-mode-semantics).
6. If `manifest.mode` is present and unrecognized, **MUST NOT** silently fall back to `document` mode. **SHOULD** fail with `ERR_MODE_UNSUPPORTED`.
7. If `manifest.mode` is absent, **MUST** treat the archive as `mode: "document"`.
8. If manifest `cover` is present but references a missing file, **SHOULD** ignore `cover` and continue processing the archive; **MAY** emit a warning.
9. **MUST** resolve asset and document links relative to the referencing file's location within the archive.
10. **MUST** reject or safely handle any path that traverses outside the archive root.
11. **MUST** accept text files that use LF (`\n`) or CRLF (`\r\n`) line endings.
12. If `spec.version` is present, **MUST** reject files where the manifest `spec.version` major version exceeds the consumer's supported major version.
13. **MUST** accept draft `1.0.x` dual-form timestamp metadata for `created` and `modified` (ISO 8601 string form or object form with required `when`).

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
  "spec": { "name": "mdzip-spec", "version": "1.1.0" },
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
3. Normalize text line endings to LF (`\n`) where practical.
4. Validate file paths against [Section 5.4](#54-path-constraints).
5. If `manifest.json` is present:
   - for producer-generated manifests, verify required field `spec.version`;
   - verify `entryPoint`, if present, exists in the archive;
   - preserve unknown fields as-is when round-tripping.
6. Ensure at least one unambiguous entry point condition from [Section 5.5](#55-entry-point-discovery) is satisfied.
7. Create an unencrypted ZIP archive and use `.mdz` extension.

### 16.2 Consumer Load Checklist

When opening a `.mdz` archive, a consumer can follow this sequence:

1. Open archive as ZIP and reject encrypted/password-protected entries.
2. Enumerate entries and validate path safety constraints ([Section 5.4](#54-path-constraints)).
3. Parse `manifest.json` if present, ignoring unknown fields.
4. Check `manifest.mode`: apply declared mode per [Section 5.7](#57-mode-semantics); default to `document` if absent; fail with `ERR_MODE_UNSUPPORTED` if unrecognized.
5. Accept `created` and `modified` in either draft `1.0.x` form (ISO 8601 string or object with required `when`).
6. If manifest `cover` is present and references a missing file, ignore `cover` and optionally warn.
7. Resolve primary Markdown file via [Section 5.5](#55-entry-point-discovery).
8. Parse Markdown with UTF-8 decoding and accept LF/CRLF text files.
9. Resolve relative links per [Section 9](#9-linking-and-references), rejecting escape attempts outside archive root.
10. If no unambiguous entry point exists, show explicit error or user choice (do not auto-pick arbitrarily).

### 16.3 Terminology Alignment (Producer vs. Create)

Normative specification text uses role terms (`producer`, `consumer`). Implementation APIs and commands may use action-oriented names such as `create` and `add`.

Recommended mapping:

- a `create` API/command is a producer operation;
- an `add` API/command is also a producer operation when adding files to a new or existing archive.

### 16.4 Archive Update Semantics (Non-Normative)

When a producer supports adding files to an existing `.mdz` archive:

- path uniqueness should be preserved in the final emitted archive (avoid duplicate logical paths);
- adding a file to an existing path should replace that path's current entry in the resulting archive, rather than retaining duplicate ZIP entries for the same path;
- after successful updates, producers should refresh timestamp metadata (`modified`, and `created` only when creating a new archive);
- when rewriting `manifest.json`, producers should preserve unknown fields.

### 16.5 Suggested Error Categories

Implementations may expose stable error categories to simplify debugging and cross-tool behavior comparisons:

- `ERR_ZIP_INVALID`: archive is not a valid ZIP container.
- `ERR_ZIP_ENCRYPTED`: archive or entries use unsupported encryption.
- `ERR_PATH_INVALID`: one or more entry paths violate [Section 5.4](#54-path-constraints).
- `ERR_MANIFEST_INVALID`: `manifest.json` is malformed or missing required fields when present.
- `ERR_ENTRYPOINT_UNRESOLVED`: no unambiguous primary Markdown file can be determined.
- `ERR_ENTRYPOINT_MISSING`: `entryPoint` references a file not present in archive.
- `ERR_VERSION_UNSUPPORTED`: manifest `spec.version` major version is not supported.
- `ERR_DUPLICATE_PATH`: duplicate logical archive paths were detected after an update operation.
- `ERR_MODE_UNSUPPORTED`: the manifest declares a `mode` value that the consumer does not support or does not recognize.

### 16.6 AI Agent Prompting Tips

To improve deterministic implementation quality, AI prompts should explicitly include:

- the exact target spec version (`1.1.0-draft` or later);
- whether producer, consumer, or both are being implemented;
- required conformance scope (minimum MUSTs vs. SHOULDs included);
- required behavior for ambiguous entry points;
- explicit test expectations from [`tests/README.md`](tests/README.md).

---

## 17. Future Extensions (Non-Normative)

This section records possible future directions and does not define current conformance requirements for `1.1.0-draft`.

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

Embedding "last read" data directly inside `.mdz` is not part of this draft and should be avoided unless a future version defines explicit multi-writer and conflict-resolution semantics.

### 17.3 Bookmarks

A future ecosystem convention may define bookmark support so readers can save and return to notable locations within MDZip documents.

As with resume state, bookmark data is best treated as consumer-local user state by default. Implementations should prefer:

- local per-user bookmark storage keyed by document identity,
- bookmark targets that can survive minor content edits where possible,
- non-destructive behavior for read-only archives.

Embedding bookmark data directly inside `.mdz` is not part of this draft and should be avoided unless a future version defines portable bookmark anchoring and conflict-resolution semantics.

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

