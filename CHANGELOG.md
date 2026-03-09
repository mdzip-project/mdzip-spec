# Changelog

All notable changes to this project are documented in this file.

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
