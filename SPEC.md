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
12. [Conformance](#12-conformance)
13. [Examples](#13-examples)

---

## 1. Overview

The **Markdown Zip** format (`.mdz`) is a portable, self-contained document format that packages one or more Markdown content files together with their associated assets—such as images, stylesheets, and other referenced resources—into a single ZIP archive.

A `.mdz` file allows authors to distribute complete Markdown-based documents without broken asset references, and enables readers and tools to reliably open and render the document without external dependencies.

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

---

## 3. Terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

| Term | Definition |
|------|-----------|
| **Archive** | The `.mdz` file itself; a ZIP-format container. |
| **Entry point** | The primary Markdown file a reader or tool opens first. |
| **Manifest** | The `manifest.json` file at the root of the archive describing the document. |
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

---

## 5. Archive Structure

The archive **MUST** contain a `manifest.json` file at the root level. All other files are organized relative to the archive root.

### 5.1 Required Files

| Path | Description |
|------|-------------|
| `manifest.json` | Document manifest (see [Section 6](#6-manifest-file)). |
| *(entry point)* | The Markdown file identified as the entry point in the manifest. |

### 5.2 Recommended Layout

```
document.mdz (ZIP archive)
├── manifest.json          # Required: document manifest
├── index.md               # Entry point Markdown file (name configurable)
├── chapter-01.md          # Additional Markdown files (optional)
├── chapter-02.md
└── assets/                # Recommended directory for non-Markdown files
    ├── images/
    │   ├── cover.png
    │   └── diagram.svg
    └── styles/
        └── style.css
```

### 5.3 Path Constraints

- All file paths inside the archive **MUST** be relative to the archive root.
- File paths **MUST NOT** begin with a leading slash (`/`).
- File paths **MUST NOT** contain path traversal sequences (e.g., `../`).
- File paths **SHOULD** use lowercase characters.

---

## 6. Manifest File

The manifest file **MUST** be named `manifest.json` and placed at the root of the archive. It **MUST** be a valid [JSON](https://www.rfc-editor.org/rfc/rfc8259) document encoded in UTF-8.

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

### 6.2 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mdz` | string | **REQUIRED** | The version of this specification the file conforms to. **MUST** be a [Semantic Versioning 2.0.0](https://semver.org/) string (e.g., `"1.0.0"`). |
| `title` | string | **REQUIRED** | The human-readable title of the document. **MUST NOT** be empty. |
| `entryPoint` | string | **REQUIRED** | Archive-root-relative path to the primary Markdown file (e.g., `"index.md"`). The referenced file **MUST** exist in the archive. |
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

A `.mdz` archive **MAY** contain multiple Markdown files, allowing a document to be split across chapters, sections, or pages. When multiple Markdown files are present, the file identified by `entryPoint` in the manifest is the primary document. Other Markdown files **SHOULD** be linked from the entry point or from other Markdown files within the archive using relative paths.

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

---

## 11. Versioning

### 11.1 Specification Versioning

This specification uses [Semantic Versioning 2.0.0](https://semver.org/):

- **Major version** increments indicate breaking, backwards-incompatible changes to the format.
- **Minor version** increments indicate backwards-compatible additions or clarifications.
- **Patch version** increments indicate corrections or editorial changes with no impact on format compatibility.

### 11.2 Manifest `mdz` Field

The `mdz` field in `manifest.json` identifies the version of this specification that the producing tool targeted. Conforming consumers:

- **MUST** reject files where the `mdz` field major version is higher than the highest major version the consumer supports.
- **SHOULD** warn users when the `mdz` field major version is lower than the consumer's current major version support.
- **MUST** accept files where the `mdz` field minor or patch version differs from the consumer's supported version, provided the major version matches.

---

## 12. Conformance

### 12.1 Conforming Producer

A conforming producer is any software that creates `.mdz` files. A conforming producer:

1. **MUST** produce a valid ZIP archive as defined in [Section 4](#4-file-format).
2. **MUST** include a `manifest.json` at the archive root containing all **REQUIRED** fields as defined in [Section 6](#6-manifest-file).
3. **MUST** include the file referenced by `entryPoint` in the archive.
4. **MUST** use UTF-8 encoding for all Markdown and JSON files.
5. **MUST** use forward-slash path separators in the archive.
6. **MUST NOT** include path traversal sequences in any file path.
7. **SHOULD** include all assets referenced by the document's Markdown content.

### 12.2 Conforming Consumer

A conforming consumer is any software that reads and/or renders `.mdz` files. A conforming consumer:

1. **MUST** be able to open and extract a valid ZIP archive.
2. **MUST** parse the `manifest.json` file and use the `entryPoint` field to identify the primary Markdown file.
3. **MUST** ignore unrecognized fields in `manifest.json`.
4. **MUST** resolve asset and document links relative to the referencing file's location within the archive.
5. **MUST** reject or safely handle any path that traverses outside the archive root.
6. **MUST** reject files where the manifest `mdz` major version exceeds the consumer's supported major version.

---

## 13. Examples

### 13.1 Minimal `.mdz` Archive

A valid minimal `.mdz` archive contains only `manifest.json` and one Markdown file:

**Archive contents:**
```
hello.mdz
├── manifest.json
└── index.md
```

**`manifest.json`:**
```json
{
  "mdz": "1.0.0",
  "title": "Hello World",
  "entryPoint": "index.md"
}
```

**`index.md`:**
```markdown
# Hello World

This is a minimal Markdown Zip document.
```

---

### 13.2 Document with Assets

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

*End of Specification*
