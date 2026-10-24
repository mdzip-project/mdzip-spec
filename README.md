# MDZip Specification

Specification for the **MDZip** (`.mdz`) file format.

Current release: `v1.2.0` (dated `2026-10-13`) — see [CHANGELOG.md](CHANGELOG.md).

This repository defines the `.mdz` file format specification; it does not provide an editor, viewer, or reference implementation.

## What is .mdz?

An `.mdz` file is a portable, self-contained document format that packages one or more Markdown content files together with their associated assets (images, stylesheets, etc.) into a single ZIP archive.

## Specification

Read the full specification: **[SPEC.md](SPEC.md)**

The specification covers:

- **File format** - ZIP-based archive structure and encoding requirements
- **Archive layout** - Required and recommended file organization
- **Manifest** - `manifest.json` metadata, entry point, and mode declaration (written by producers, never required by consumers)
- **Modes** - `document` (default) and `project` interpretation modes
- **Markdown content** - Encoding, dialect guidance, and multi-page support
- **Assets** - Bundling images and other resources
- **Linking** - How to reference files within the archive
- **MIME type** - Proposed `application/vnd.mdzip` with the `.mdz` extension
- **Versioning** - Semantic versioning of the spec and compatibility rules
- **Conformance** - Requirements for producers and consumers

## Repository Contents

- [SPEC.md](SPEC.md) - canonical format specification
- [fixtures/](fixtures/README.md) - shared conformance fixtures: test catalog, prebuilt archives and machine-readable cases
- [examples/](examples/README.md) - non-normative templates, guidance and design rationale
- [schema/](schema/manifest-1.2.0.schema.json) - versioned JSON Schema companion for manifest validation
- [CHANGELOG.md](CHANGELOG.md) - project change history
- [CONTRIBUTING.md](CONTRIBUTING.md) - contribution process

## Quick Start

A minimal `.mdz` file is a ZIP archive (renamed with an `.mdz` extension) containing:

1. **`index.md`** at the archive root. Without a manifest, consumers open `index.md`; failing that, the only Markdown file at the root, setting aside support files such as `README.md` and `AGENTS.md` (see SPEC.md §5.5):

   ```markdown
   # My Document

   Hello from MDZip!
   ```

2. **`manifest.json`** for metadata and the entry point. It's optional when you zip a folder by hand, and required in archives written by MDZip software (conforming producers). This example uses the current release, 1.2.0:

   ```json
   {
     "spec": {
       "name": "mdzip-spec",
       "version": "1.2.0"
     },
     "title": "My Document",
     "mode": "document",
     "entryPoint": "index.md"
   }
   ```

## License

This project is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
See [LICENSE](LICENSE).

## Contributing

Feedback, questions, and proposals are welcome via this repository's issue tracker.
