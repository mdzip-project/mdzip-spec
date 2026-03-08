# markdownzip-spec

Specification for the **Markdown Zip** (`.mdz`) file format.

## What is .mdz?

A `.mdz` file is a portable, self-contained document format that packages one or more Markdown content files together with their associated assets (images, stylesheets, etc.) into a single ZIP archive.

## Specification

📄 **[Read the full specification → SPEC.md](SPEC.md)**

The specification covers:

- **File format** – ZIP-based archive structure and encoding requirements
- **Archive layout** – Required and recommended file organization
- **Manifest** – The `manifest.json` schema describing the document's metadata
- **Markdown content** – Encoding, dialect guidance, and multi-page support
- **Assets** – Bundling images and other resources
- **Linking** – How to reference files within the archive
- **MIME type** – `application/vnd.markdownzip` with the `.mdz` extension
- **Versioning** – Semantic versioning of the spec and compatibility rules
- **Conformance** – Requirements for producers and consumers

## Quick Start

A minimal `.mdz` file is a ZIP archive containing:

1. **`manifest.json`** at the archive root:

   ```json
   {
     "mdz": "1.0.0",
     "title": "My Document",
     "entryPoint": "index.md"
   }
   ```

2. **`index.md`** (or whatever path is set as `entryPoint`):

   ```markdown
   # My Document

   Hello from Markdown Zip!
   ```

## Contributing

This specification is in draft status. Feedback, questions, and proposals are welcome via [issues](../../issues).
