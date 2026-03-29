# MDZip Specification

Specification for the **MDZip** (`.mdz`) file format.

Current draft release: `v1.0.1-draft` (dated `2026-03-29`).

This repository defines the `.mdz` file format specification; it does not provide an editor, viewer, or reference implementation.

## What is .mdz?

An `.mdz` file is a portable, self-contained document format that packages one or more Markdown content files together with their associated assets (images, stylesheets, etc.) into a single ZIP archive.

## Specification

Read the full specification: **[SPEC.md](SPEC.md)**

The specification covers:

- **File format** - ZIP-based archive structure and encoding requirements
- **Archive layout** - Required and recommended file organization
- **Manifest** - Optional `manifest.json` metadata and entry-point override
- **Markdown content** - Encoding, dialect guidance, and multi-page support
- **Assets** - Bundling images and other resources
- **Linking** - How to reference files within the archive
- **MIME type** - Proposed `application/vnd.mdzip` with the `.mdz` extension
- **Versioning** - Semantic versioning of the spec and compatibility rules
- **Conformance** - Requirements for producers and consumers

## Repository Contents

- [SPEC.md](SPEC.md) - canonical format specification
- [examples/](examples/README.md) - sample valid and invalid package structures
- [tests/](tests/README.md) - conformance case catalog and expected behavior
- [schema/](schema/manifest-1.0.1-draft.schema.json) - versioned JSON Schema companion for manifest validation
- [reference/](reference/README.md) - non-normative notes and rationale
- [CHANGELOG.md](CHANGELOG.md) - project change history
- [CONTRIBUTING.md](CONTRIBUTING.md) - contribution process

## Quick Start

A minimal `.mdz` file is a ZIP archive (renamed with a `.mdz` extension) containing:

1. **`index.md`** at the archive root (for a single `.md` file, it can have any valid name. `index.md` will take precedence if there are multiple files and no manifest):

   ```markdown
   # My Document

   Hello from MDZip!
   ```

2. *(Optional)* **`manifest.json`** for metadata and entry-point override:

   ```json
   {
     "spec": {
      "name": "mdzip-spec",
       "version": "1.0.1"
     },
     "title": "My Document",
     "entryPoint": "index.md"
   }
   ```

## License

This project is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
See [LICENSE](LICENSE).

## Contributing

This specification is in draft status. Feedback, questions, and proposals are welcome via this repository's issue tracker.
