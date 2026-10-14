# tests

Conformance test catalog for `.mdz` producers and consumers.

## Test Matrix

| ID | Case | Input | Expected Result |
|----|------|-------|-----------------|
| `T-001` | Minimal valid package | `examples/minimal/` | Consumer opens `index.md` as primary document. |
| `T-002` | Valid package with manifest | `examples/with-manifest/` | Consumer uses `manifest.json.entryPoint`. |
| `T-003` | Manifest entryPoint target missing; only a support file remains | `examples/invalid/missing-index/` | Consumer rejects with `ERR_ENTRYPOINT_MISSING`: manifest declares `entryPoint: "index.md"` but that file is not present in the archive. It **MUST NOT** silently open `README.md` instead. Recovering to `README.md` (Section 5.5 rules 2–4) passes only with a visible warning. |
| `T-004` | Manifest points to missing file | `examples/invalid/bad-entrypoint/` | Consumer rejects with `ERR_ENTRYPOINT_MISSING` (`entryPoint: "missing.md"`). It **MUST NOT** silently open `index.md` instead. Recovering to `index.md` passes only with a visible warning. |
| `T-005` | CRLF text file handling | `examples/line-endings-crlf/` | Consumer accepts and reads document. |
| `T-006` | Support files in entry point discovery | `examples/fixtures/entrypoint-cases.json` (support-file cases) | Consumer sets aside root-level `README`, `AGENTS`, `LICENSE`, `CHANGELOG` and `CONTRIBUTING` files (case-insensitive, `.md`/`.markdown`) when applying rule 3 of Section 5.5, and resolves each case to its `expectedEntryPoint`. |
| `T-007` | Archive without a manifest | `examples/minimal/` | Consumer opens the archive; it does not reject or warn as non-conforming because `manifest.json` is missing. |
| `T-008` | Invalid vs. missing `entryPoint` | `examples/fixtures/entrypoint-cases.json` (cases with `expectedError`) | Consumer reports `ERR_ENTRYPOINT_INVALID` for malformed values (non-string, empty, absolute, traversal, backslash, directory, non-Markdown) and `ERR_ENTRYPOINT_MISSING` for valid paths with no matching entry, including case-only differences; it never silently falls back. |
| `T-009` | Path matching | `examples/fixtures/path-matching-cases.json` | Consumer matches NFC-normalized paths case-sensitively: NFC and NFD forms of the same path match, and there is no case folding (`ß`/`ss`, Greek final sigma, Turkish dotless `ı`). |
| `T-010` | Locale-independent support-file detection | `LICENSE.md` + `notes.md`, with the process locale set to Turkish (`tr-TR`) | Entry point is `notes.md`: support file names are compared ASCII case-insensitively, not with locale rules (which lowercase `LICENSE` to `lıcense`). |
| `T-011` | Link resolution inside, outside and into archives | `examples/fixtures/link-resolution-cases.json` | Consumer resolves each link to the expected `kind` and target (Sections 9.3–9.5). Consumers that don't support links outside or into archives run the cases with `outsideLinks` / `intoArchiveLinks` set to `false` and must get `unresolved` — never a different target, and never a `..` clamped at the archive root. Targets outside the trust boundary are `denied` whether or not they exist, and resources the document embeds from outside the archive are `denied` unless enabled (Section 9.6). Entry names like `../escape.md` stay invalid (`path-validation-cases.json`). |
| `T-012` | Manifest validation | `examples/fixtures/manifest-cases.json` | Consumer rejects unreadable manifests and invalid critical fields (`spec`, `spec.version`, `mode`, `entryPoint`) with the listed error, ignores invalid descriptive fields, reads the last of duplicate members and reports them (Section 6.4). |
| `T-013` | Whole-archive entry names | `examples/fixtures/entry-set-cases.json` | Consumer rejects NFC duplicates (`ERR_DUPLICATE_PATH`) and a file that is also a directory (`ERR_PATH_CONFLICT`); it never picks one entry or renames one (Sections 5.4, 13.1). |
| `T-014` | Unsupported compression method | `examples/fixtures/unsupported-compression.mdz` (case `unsupported-compression` in `archive-cases.json`) | `index.md` uses BZIP2 (method 12). Consumer reads methods 0 and 8; for any other method it either rejects the archive with `ERR_ZIP_INVALID` or, if it supports the method, reads the entry correctly. It never shows the entry empty or garbled, or treats it as missing (Section 4). |
| `T-015` | Project mode | `examples/fixtures/project-mode.mdz` (case `project-mode` in `archive-cases.json`) | A project-capable consumer opens `index.md` and each document on its own, never joined (Sections 5.7.2, 5.7.3). A document-only consumer fails with `ERR_MODE_UNSUPPORTED`, or opens the entry point as a document after a user-visible warning; it never falls back silently (Section 5.7.6). |
| `T-016` | Hostile content | `examples/fixtures/hostile-content.mdz` with `hostile-content-cases.json` | Rendering the entry point runs no script from the archive (`<script>`, event-handler attributes, inline and file SVG scripts, `javascript:` links), ignores the document's `<base>` element, and makes none of the listed requests to the canary origin; the archive's own image still renders. MUST cases cover Sections 9.3 and 13.2; SHOULD cases cover automatic loading over `http:` (Section 9.2) and automatic redirects (Section 13.2). Rendering consumers only: libraries that don't render skip it. |
| `T-017` | Symbolic link entries | `examples/fixtures/symlink-entries.mdz` (case `symlink-entries` in `archive-cases.json`) | `shortcut.md`, `linked` and `escape.md` are symbolic links (to `notes.md`, `docs` and a path outside the archive). Consumer opens `index.md`, never follows a link: `shortcut.md` and `escape.md` are skipped or read as files containing the target text, `linked/page.md` is unresolved, and extraction creates no symbolic link and writes nothing outside the destination. It SHOULD report each one (Sections 4, 13.1). |

## Producer Checks

| ID | Case | Expected Result |
|----|------|-----------------|
| `P-001` | New archive | Archive contains `manifest.json` with `spec.version` and an `entryPoint` that references a Markdown file in the archive; `title` and `mode` are present (recommended). |
| `P-002` | Add a support file to an archive with no manifest (for example `notes.md` + new `AGENTS.md`) | Entry point still resolves to `notes.md`; the producer adds `manifest.json` with `entryPoint: "notes.md"` (recommended). |
| `P-004` | Preserve unknown manifest fields | `examples/fixtures/round-trip.mdz`: run each flow in `round-trip-expectations.json` twice. After every save, each `preservedManifestValues` pointer still holds a JSON-equal value (top-level and nested unknown fields, every JSON type, profile-like fields) (Section 6.3). |
| `P-005` | Preserve untouched entries, including `AGENTS.md` | Same flows: every `preservedEntries` file not listed in the flow's `changes` or `removes` keeps its path, byte length and SHA-256; files in `removes` must be absent. Covers a root `AGENTS.md`, a nested `docs/AGENTS.md`, a `large/AGENTS.md` over 24 KB, an unknown binary file and a CSV (Section 14.1). |
| `P-003` | Add a second support file to an archive whose only Markdown file is a support file (for example `README.md` + new `AGENTS.md`) | Producer adds `manifest.json` with `entryPoint: "README.md"`, so the entry point stays resolvable; leaving the archive ambiguous is non-conforming. |
| `P-006` | Create vs. modify a manifest-less archive | Creating an archive always writes `manifest.json`. Editing a document in an existing archive that has no manifest and saving it is conforming whether or not a manifest is added (adding one is recommended); either way the entry point still resolves to the same file (Section 14.1). |
| `P-007` | Entry names and ZIP flags | Every entry uses method 0 or 8; non-ASCII names carry the UTF-8 flag (bit 11); no empty or `.` segments, no file that is also a directory, no duplicate members in `manifest.json`; every entry is a regular file or a directory, never a symbolic link (Sections 4, 5.4, 6.4). |
| `P-008` | Modify an archive that contains symbolic links | Open `examples/fixtures/symlink-entries.mdz`, edit `notes.md` and save. The producer writes no new symbolic link. For the three existing ones it either repairs the archive with the user's agreement (removing them, or storing them as regular files) or keeps them and tells the user; it never drops them silently (Section 14.1). |

## Notes

- Each test input directory represents archive-root contents before zipping.
- A harness MAY zip each directory as `*.mdz` and validate the expected outcome.
- Add producer-side checks separately (for example, path normalization and traversal rejection).
- Prebuilt fixture archives and the JSON case files are in [`examples/fixtures/`](../examples/fixtures/); its README lists them. Archives that need symbolic links or a non-DEFLATE method are generated by [`tools/build-zip-fixtures.py`](../tools/build-zip-fixtures.py).
