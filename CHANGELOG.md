# Changelog

All notable changes to this project are documented in this file.

## [1.0.1-draft] - 2026-03-16

### Changed

- Migrated manifest compatibility metadata from top-level `mdz` to `spec.version` (with optional `spec.name`).
- Added producer provenance structure with separate application/core tracks:
  - `producer.application.{name,version,url}`
  - `producer.core.{name,version,url}`
- Added optional author contact/profile metadata under `author.{name,email,url}`.
- Updated consumer versioning rules to key off `spec.version` when present and treat missing version metadata as unknown (non-fatal baseline compatibility path).
- Updated conformance language to require `spec.version` for conforming producer-generated manifests and recommend producer/author URL/email metadata when appropriate.
- Allowed draft transitional `modified` dual-form handling: ISO 8601 string (legacy) or object form with `modified.when` and optional `modified.by`.
- Aligned `created` with `modified` in draft `1.0.x`: both fields now allow string ISO 8601 form or object form with required `when` and optional `by`.
- Added non-normative terminology alignment guidance mapping implementation actions (`create`, `add`) to producer operations.
- Added non-normative archive update guidance for add/update flows (replace semantics, duplicate-path avoidance, manifest round-trip behavior).
- Added versioned JSON Schema companion at `schema/manifest-1.0.1-draft.schema.json` and linked it from spec Section 6.
- Updated examples and README manifest snippets to the new schema.
- Bumped draft version in `SPEC.md` to `1.0.1-draft` (dated `2026-03-16`).

## [1.0.0-draft] - 2026-03-08

### Added

- Initial draft specification in [SPEC.md](SPEC.md).
- Optional `manifest.json` model with required `index.md` root entry point.
- LF/CRLF interoperability rules (producer `SHOULD` write LF; consumer `MUST` accept LF/CRLF).
- Example and conformance scaffolding under `examples/` and `tests/`.
- Project license under CC BY 4.0 in [LICENSE](LICENSE).
- Contributor workflow in [CONTRIBUTING.md](CONTRIBUTING.md).
- Section 5.5: fallback behavior of `index.md` when manifest `entryPoint` overrides it, with stub example and producer guidance.
- Section 5.4: path constraints for null bytes, ASCII control characters, and OS-reserved characters (`\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`) for cross-platform safety.
- Non-goal: ordered navigation, pagination, and TOC structure for multi-page documents explicitly out of scope.
- `reference/README.md`: design rationale and background notes for key specification decisions.
- Manifest schema: required fields (`mdz`, `title`) now annotated inline above Section 6.2 field table.

### Changed

- Standardized terminology to use `assets/` and `manifest.json`.
- Clarified behavior for archives without `manifest.json`.
- Added provisional MIME registration note for `application/vnd.markdownzip`.
- Clarified `index.md` as a required fallback entry point (not merely the default), always present regardless of manifest `entryPoint`.
- Updated Section 14.1 conforming producer requirements to include stub guidance (item 4).
- Replaced mandatory `index.md` requirement with a four-step entry point discovery algorithm (Section 5.5). `index.md` is now the recommended convention, not a hard requirement.
- Consumers MUST NOT silently pick an entry point when ambiguous; SHOULD present user with file list or clear error.
- Updated Sections 5, 5.1, 5.2, 5.3, 6.2, 12.1, 14.1, 14.2, and 15.1 to reflect the new discovery model.
