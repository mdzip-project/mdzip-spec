# Changelog

All notable changes to this project are documented in this file.

## [1.2.0-draft] - Unreleased

### Added

- `schema/manifest-1.2.0.schema.json`: requires `spec.version` and `entryPoint` (what a 1.2.0 producer MUST write) and gives `entryPoint` a pattern for a valid entry point path (Section 5.5: relative, optional leading `./`, no `..` segments, no reserved or control characters, `.md`/`.markdown` ASCII case-insensitive, no empty or `.` segments) and a matching path pattern for `cover`. The patterns agree with every `entryPoint` in `entrypoint-cases.json` and every `cover` in `manifest-cases.json`. Consumers must not use the schema to reject archives.
- Section 5.8: optional root-level `AGENTS.md` — guidance for AI agents and tools that open an archive without native `.mdz` support. Advisory only; `manifest.json` stays authoritative. Sample at `examples/templates/AGENTS.sample.md`. ([#5](https://github.com/mdzip-project/mdzip-spec/issues/5))
- **Support file** term (Section 3) and closed support-file list in Section 5.5: `README`, `AGENTS`, `LICENSE`, `CHANGELOG`, `CONTRIBUTING` (case-insensitive, `.md` or `.markdown`, root level only). ([#5](https://github.com/mdzip-project/mdzip-spec/issues/5))
- Section 5.4.1: path matching rules for every archive lookup (`entryPoint`, `cover`, `index.md`, links). Paths are compared **case-sensitively after Unicode NFC normalization**, so NFC and NFD forms of the same name match (resolves the normalization half of [#4](https://github.com/mdzip-project/mdzip-spec/issues/4)). Case-insensitive comparison is limited to fixed ASCII names (`.md`/`.markdown`, support file names) and MUST NOT use locale-sensitive case conversion. Consumers MAY suggest a case-only near match but MUST NOT use it silently.
- Section 5.4: archives MUST NOT contain two entries equal after NFC normalization and SHOULD NOT contain entries differing only in case (they collide on case-insensitive filesystems); the lowercase-path recommendation now applies only to writing systems that have case. Producers SHOULD write NFC paths (Sections 4, 14.1). Consumers SHOULD report NFC-duplicate entries as `ERR_DUPLICATE_PATH` and detect extraction collisions (Section 13.1).
- Section 9.3: a single link resolution algorithm — fragments separated, destinations split on `/` and percent-decoded per segment (so `%2F` can't create a path step), dot segments applied from the referencing file's directory. Unresolvable links stay unresolved and are never redirected; `..` is never clamped at the archive root.
- Section 9.4 (optional): **links outside the archive.** A relative link that climbs above the archive root continues in the directory containing the `.mdz` file (the archive root is a virtual directory at the archive's location), e.g. `../Notes.md` from `index.md`. Unresolved when unsupported, when the archive has no host location (opened from bytes), or when the target is missing or access is denied. Host-side matching follows the host filesystem.
- Section 9.5 (optional): **links into archives.** A path segment naming an existing MDZip archive (`.mdz`, ASCII case-insensitive) is an archive boundary: `Project.mdz/chapters/intro.md#background`, or `Project.mdz` for its entry point. At most one entered boundary per link; `..` above an entered archive's root is unresolved. Ordinary relative links, no URI scheme. Stable identifier for graphs: host path of the archive plus entry path.
- Section 9.6: links beyond an archive are navigation only (no extraction or writes), respect host trust boundaries, SHOULD warn before leaving the workspace/vault, and make an archive location-dependent; producers MUST NOT rewrite them, and validators SHOULD report them as informational notices.
- Section 9.7: **other link syntaxes are explicitly allowed.** Sections 9.3–9.5 (including "don't substitute a different target") govern standard Markdown link destinations only — inline/reference links and images, and HTML `href`/`src`. Wikilinks (`[[Page]]`), embeds (`![[image.png]]`) and other dialect- or host-defined syntaxes MAY be used and resolved by their own rules, including name lookup. Name-based lookups SHOULD consider the archive's own documents first; unsupported syntaxes SHOULD be left intact; Section 9.6 still applies to links leaving the archive. Section 12.4 cites them as dialect-specific features to document.
- `tools/sync-fixtures.mjs`: copies `examples/fixtures/` from a released spec tag into an implementation's tests and writes a `SPEC-FIXTURES.json` marker (tag, commit, SHA-256 per file); `--check` detects hand-edited or stale copies. `examples/fixtures/README.md` documents using it, pinning to tags, and keeping implementation-specific cases in separate files.
- Entry point fixtures: a malformed manifest is given as raw text in `manifestJson` (with `manifest: null`), so implementations that load `manifest` into a typed model can still read the file.
- Fixture `examples/fixtures/link-resolution-cases.json` (33 cases) and test `T-011`. Based on the planning proposal "External relative Markdown links in MDZip" (2026-10-10).
- Section 5.5: definition of a valid entry point path, and new error `ERR_ENTRYPOINT_INVALID` (Section 16.5) for malformed values — non-string, empty, absolute, traversal, backslash, directory, or non-Markdown. `ERR_ENTRYPOINT_MISSING` now means a valid path that matches no entry, including a case-only difference.
- Fixtures: `examples/fixtures/path-matching-cases.json`; invalid/missing/case/NFC cases in `entrypoint-cases.json`; tests `T-008`–`T-010`.
- Section 6.3: producers rewriting `manifest.json` MUST preserve unrecognized fields — top level and inside recognized objects, every JSON value type — unless the user asks to remove them. Preservation is semantic (JSON-equal), not textual; producers using closed typed models MUST retain unknown data. Previously only non-normative guidance (Sections 16.1, 16.4).
- Section 14.1: modifying producers MUST preserve every archive entry they don't intend to change — including `AGENTS.md`, nested support files, unknown file types — byte-for-byte, and SHOULD keep and surface content they can't display rather than dropping it on save.
- Round-trip fixture: `examples/round-trip/`, `examples/fixtures/round-trip.mdz` and `round-trip-expectations.json` (JSON-Pointer manifest checks and SHA-256 entry checks over five open/edit/save flows); tests `P-004`, `P-005`; `.gitattributes` keeps fixture bytes stable.
- Section 14.1: requirements for producers that modify an existing archive — MUST NOT change or break entry point resolution; SHOULD add a missing manifest; MUST preserve unrecognized manifest fields and untouched entries (see below). ([#6](https://github.com/mdzip-project/mdzip-spec/issues/6))
- Conformance cases: support-file entry point cases in `examples/fixtures/entrypoint-cases.json`; `T-006`, `T-007` and producer checks `P-001`–`P-003` in `tests/README.md`.

### Changed

- Conformance test `T-016` (hostile content) with `examples/hostile-content/`, `fixtures/hostile-content.mdz` and `fixtures/hostile-content-cases.json`: twelve cases (scripts, event handlers, inline and file SVG scripts, `javascript:` links, `<base>`, meta refresh, and automatic `http:` loads by stylesheets, `style`, iframes, objects and images). Each one requests a local canary URL if it gets through, so a harness only needs a small HTTP server. Rendering consumers only.
- Sections 4 and 13.1: symbolic links. Every entry MUST be a regular file or a directory, and producers MUST NOT write symbolic links or other special files. Consumers MUST NOT follow a symlink entry (no link created on extraction, no path or Markdown link resolved through it, even to a target inside the archive); they SHOULD report it and MAY skip it or read it as a file containing the target text. Was "SHOULD ignore or safely handle". Unicode file names were already covered by Section 5.4.1. ([#4](https://github.com/mdzip-project/mdzip-spec/issues/4))
- Section 9.2: automatically loaded external resources (such as `![logo](https://example.com/logo.png)`) reveal to their server that the document was opened and make the archive not self-contained. Consumers SHOULD let users turn this loading off and SHOULD NOT load over unencrypted `http:`; producers and validators MAY report external resources as informational notices. Closes the gap with Section 9.6, which already limited automatic loading of local files outside the archive. Also a Section 13.2 bullet.
- Section 9.3: heading anchors are dialect-defined (`#my-heading` on GitHub, `#My Heading` in Obsidian); a fragment that matches no anchor still resolves to its target document.
- New Section 14.3 Conformance Fixtures: implementations SHOULD run the shared fixtures pinned to a released tag; the fixtures are non-normative, the prose governs when they disagree (a disagreement is a fixture defect), and passing them all does not by itself make an implementation conforming. Matches the existing rule that the prose wins over the JSON Schema (Section 6).
- Third external review:
  - Section 9.6 trust boundary: links outside or into archives reach only targets inside a location the user trusts (a vault or workspace), unless the user allows a specific target; a target outside it is unresolved whether or not it exists. Automatic loading of resources from outside an archive is off by default and never allowed outside the boundary. The section now names local-file disclosure as the threat. Link fixtures gain `trustRoot`, `allowedPaths`, `loadOutsideResources`, `use: "embed"` and the reason `denied`.
  - Section 14.1: conformance belongs to the archive written. A modification MUST NOT introduce violations of Sections 4, 5.4 or 6; saving an archive that already has one requires repairing it with the user's agreement or telling the user, never a silent drop or rename.
  - Sections 3, 8 and 13.3: an *asset* (or *resource*) is any non-Markdown file the archive uses, including files used by the manifest (`cover`) or an extension, not only files linked from Markdown. Section 8.3 now discourages genuinely unused files only.
  - Section 11.1: compatibility is defined for archives, not implementations; a minor version may add implementation requirements.
  - Section 6.2: an omitted `language` is unspecified (was "defaults to `en`"); consumers may fall back to a default of their choice but shouldn't report it as the document's language.
  - Section 6.1: `created`/`modified` datetimes use RFC 3339 `date-time` (was "ISO 8601"), matching the JSON Schema; other forms are invalid descriptive values.
  - Schema: `spec.version` uses the semver.org regular expression (the previous pattern accepted `1.2.0-01`). New `manifest-cases.json` cases for SemVer and RFC 3339.
  - Section 9.5: the host path + entry path is a host-relative identifier that changes when the archive moves (was "stable identifier"). Section 2: goal reworded from "renderable by any tool" to "readable and inspectable". README Quick Start reflects the manifest rule and the support-file entry point rules.
- Second external review: tightened the behavioral contract without adding features.
  - Section 5.7.2: document mode now means "open the entry point"; links to other Markdown files don't imply inclusion, concatenation or reading order, and no inclusion mechanism is defined. A unified view stays optional. Section 5.7.3: project documents are independently addressable.
  - Section 14.2 item 5 now includes the Section 5.7.6 exception (a recognized but unsupported mode may fall back with a visible warning; no user approval needed).
  - New Section 6.4 Manifest Validation (examples are now 6.5): unreadable manifests are `ERR_MANIFEST_INVALID`; critical fields (`spec`, `spec.version`, `mode`, `entryPoint`) with a wrong type or value are errors; descriptive fields are ignored; `null` is a wrong type; producers MUST NOT write duplicate member names, and consumers that accept them use the last.
  - Section 14.1: producer operations are *creation* or *modification*; saving a manifest-less archive without adding a manifest is conforming (adding one stays a SHOULD).
  - Section 5.4: no empty or `.` segments; file paths don't end in `/` (directory entries are optional); a file may not also be a directory (new `ERR_PATH_CONFLICT`); valid names may still be unextractable on some filesystems (`CON.md`), which extractors report rather than rename.
  - Section 4: entries MUST use method 0 or 8 and consumers MUST support both; ZIP64 only when a field overflows (including > 65,535 entries); producers set the UTF-8 flag for non-ASCII names; the central directory wins over local headers.
  - Section 13.1: entries violating Section 5.4 are never extracted under their names or silently renamed (was "reject or sanitize"); consumers MUST NOT choose between NFC duplicates or conflicting entries.
  - Section 9.3: the fragment is split at the first `#` before removing `?query`; a query-only link is the current document; queries never choose the target; invalid percent-encoding is unresolved; decode once; `%23` stays in the name; empty segments are ignored; a trailing `/` names a directory; HTML `<base>` is ignored.
  - Section 9.6: beyond-archive links are *read-only* (was "navigation only", which contradicted Section 9.4 allowing images); navigation and automatic loading are distinguished.
  - Section 11.2: consumers MUST NOT reject solely for a minor/patch difference (was "MUST accept", which over-promised).
  - Smaller: the overview no longer promises rendering without external dependencies; `created`/`modified` forms no longer scoped to "draft 1.0.x"; `cover` path syntax defined like `entryPoint`; Section 7.4 defers to Section 5.5; Section 14.2 item 1 allows reading entries without extracting; examples target 1.2.0; Section 5.8 no longer claims generic ZIP tools "cannot preserve" structure.
  - Fixtures: new `manifest-cases.json` (`T-012`) and `entry-set-cases.json` (`T-013`); link edge cases in `link-resolution-cases.json`; `.` and empty segments in `path-validation-cases.json`. Tests `T-014`, `T-015`, `P-006`, `P-007`.
- Section 5.4: removed the recommendation that file paths use lowercase. It conflicted with uppercase support files (`README.md`, `AGENTS.md`), flagged ordinary names such as `Ada Lovelace.md`, and producers can't act on it without breaking links. It is now a non-normative tip for authors. In its place, producers MUST NOT change the capitalization of source file names unless the user asks (Section 14.1 item 13, later items renumbered), and consumers SHOULD (was MAY) report a lookup that fails only because of case (Section 5.4.1).
- Section 5.4: the traversal rule now reads "entry paths MUST NOT contain `..` segments" and says it applies to stored names only, so links in Markdown may still use `../` (including to leave the archive, Section 9.4). Names that merely contain `..`, such as `notes..md`, were always allowed and now say so. Section 14.1 item 10 matches. New `path-validation-cases.json` cases cover both.
- Section 12.2: line-ending normalization now covers only Markdown files and `manifest.json` that a producer creates or modifies (previously "all text files"). Producers SHOULD NOT change line endings in other files unless the user asks (some formats depend on CRLF), MUST NOT change them in entries they don't otherwise modify (Section 14.1), and MAY offer to keep the originals. No warning is required, and no manifest field is defined. Section 4, Section 14.1 item 8 and Section 16.1 step 3 now defer to Section 12.2 instead of restating the rule.
- Section 5.5 rule 3: support files are set aside when counting root-level Markdown files. `notes.md` + `AGENTS.md` (no manifest, no `index.md`) now resolves to `notes.md` instead of being ambiguous. An archive whose only root-level Markdown file is a support file still resolves to it. Archives that resolved under 1.1.0 resolve the same way. ([#5](https://github.com/mdzip-project/mdzip-spec/issues/5))
- Manifest requirement split by role (Sections 5, 6, 14). ([#6](https://github.com/mdzip-project/mdzip-spec/issues/6))
  - Conforming producers MUST write `manifest.json`, with `spec.version` and `entryPoint` REQUIRED, and SHOULD include `title` and `mode`. Previously the manifest was optional for producers and `entryPoint` was optional.
  - Conforming consumers MUST NOT require `manifest.json`. Hand-made archives (a folder zipped and renamed) remain valid.
  - Archives from producers targeting earlier versions remain valid for consumers.
- Section 5.5 rule 1 (clarification): when the manifest declares an `entryPoint` that isn't in the archive, consumers MUST NOT silently fall back to rules 2–4 and SHOULD report `ERR_ENTRYPOINT_MISSING`; they MAY recover with rules 2–4 after a visible warning. Rules 2–4 apply only when no `entryPoint` is declared. The 1.1.0 wording ("a valid `entryPoint` … referencing an existing file") read as a silent fallthrough, contradicting tests `T-003`/`T-004` and `@mdzip/core-js`, which already reject. Sections 14.2 and 16.2 and the `T-003`/`T-004` expectations updated to match.
- Section 9.3 (was: consumers MUST reject or ignore any link resolving outside the archive root): links that leave the archive are now optional features (Sections 9.4–9.5); consumers that don't support them treat them as unresolved, which still satisfies the old rule, so existing consumers remain conforming and no archive changes meaning. Archive entry path validation and extraction rules (Sections 5.4, 13.1) are unchanged — entry names with `..` remain invalid. Hence a minor version rather than a major one.
- Section 12.3: consumers MUST (was SHOULD) match archive paths case-sensitively, now after NFC normalization. Consumers that matched case-insensitively (for example `@mdzip/core-js` for `entryPoint`) need updating; an `entryPoint` whose case differs from the entry was already non-conforming under 1.1.0 (Section 6.2 required the referenced file to exist).
- Section 6.2: `entryPoint` is now CONDITIONALLY REQUIRED (required in producer-generated manifests); `title` and `mode` note the producer recommendation.
- Examples in Sections 6.4 and 15.2 include `"mode": "document"`; Section 15.1 notes that a conforming producer would also write a manifest.

## [1.1.0] - 2026-04-05

### Added

- Section 5.7: Mode semantics — defines `document` (default) and `project` interpretation modes for `.mdz` archives.
  - `document` mode: archive represents a single logical document; entry point resolved via standard discovery algorithm; default when no manifest is present or `mode` is absent.
  - `project` mode: archive represents a collection of independent Markdown documents; requires explicit `manifest.json` with `"mode": "project"`; consumers MUST NOT flatten files into a single document.
  - Mode values are case-sensitive and MUST be lowercase.
  - Consumers MUST NOT infer mode from file count, filenames, or directory structure.
  - Unrecognized mode values: consumers MUST NOT silently fall back to `document` mode; SHOULD fail with `ERR_MODE_UNSUPPORTED`.
  - Document-only consumers MAY fall back to `document` mode when encountering `project` mode, provided they emit a clear user-visible warning.
  - Section 5.7.4: entry point semantics by mode — both modes use the standard discovery algorithm when `entryPoint` is absent.
  - Section 5.7.6: consumer support levels defined (document-only vs. full-featured).
- Manifest field `mode` (OPTIONAL): added to schema (Section 6.1) and field definitions table (Section 6.2), positioned before `entryPoint`.
- Section 6.4: added project mode manifest example.
- `ERR_MODE_UNSUPPORTED` added to suggested error categories (Section 16.5).
- Conformance Section 14.1 (producer): added requirement for `project` mode archives to satisfy entry point discovery.
- Conformance Section 14.2 (consumer): added mode recognition, unrecognized mode, and absent mode rules.
- Section 3 terminology: added **Mode**, **Document mode**, and **Project mode** definitions.
- Section 17.1: noted that `document`/`project` mode semantics address the foundational use case previously listed as a future extension.
- Section 5.3: expanded recommended layouts — existing layout labelled as document mode; added two project mode layout patterns (flat shared assets and per-section assets).
- Section 16.2 consumer checklist: added mode handling step.
- Added versioned JSON Schema companion at `schema/manifest-1.1.0.schema.json` with `mode` field as an `enum` constraint enforcing allowed values and lowercase requirement.

### Changed

- Section 8.1: asset placement recommendation changed from an `assets/` wrapper directory to flat type-named directories at the archive root (e.g., `images/`, `styles/`). An `assets/` parent directory remains permitted but is no longer recommended. Additional hierarchy within type directories is recommended when volume warrants it.
- Section 5.4: added author-facing note clarifying that path constraints are an implementor concern; added rationale explaining why ZIP's permissiveness requires tighter constraints.
- Updated all path examples and example manifests throughout the spec to reflect the flatter asset layout and current spec version.

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
- Added provisional MIME registration note for `application/vnd.mdzip`.
- Clarified `index.md` as a required fallback entry point (not merely the default), always present regardless of manifest `entryPoint`.
- Updated Section 14.1 conforming producer requirements to include stub guidance (item 4).
- Replaced mandatory `index.md` requirement with a four-step entry point discovery algorithm (Section 5.5). `index.md` is now the recommended convention, not a hard requirement.
- Consumers MUST NOT silently pick an entry point when ambiguous; SHOULD present user with file list or clear error.
- Updated Sections 5, 5.1, 5.2, 5.3, 6.2, 12.1, 14.1, 14.2, and 15.1 to reflect the new discovery model.
