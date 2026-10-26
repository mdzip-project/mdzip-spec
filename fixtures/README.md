# Shared fixtures

Executable conformance cases for `.mdz` producers and consumers: prebuilt
archives and machine-readable case files that every implementation runs, so
they all assert the same behavior. The requirements themselves are in
[`SPEC.md`](../SPEC.md); explanatory samples and guidance are in
[`examples/`](../examples/README.md).

- [Consumer tests](#consumer-tests) and [producer checks](#producer-checks) — what to run and the expected result
- [Files](#files) — the archives and case files in this folder
- [Using these fixtures in an implementation](#using-these-fixtures-in-an-implementation) — syncing them from a released tag

Only the files directly in this folder are fixtures. [`src/`](src/) holds the
folders the archives are built from; the sync tool doesn't copy it.

## Consumer tests

| ID | Case | Input | Expected Result |
|----|------|-------|-----------------|
| `T-001` | Minimal valid package | `minimal.mdz` (from `src/minimal/`) | Consumer opens `index.md` as primary document. |
| `T-002` | Valid package with manifest | `with-manifest.mdz` (from `src/with-manifest/`) | Consumer uses `manifest.json.entryPoint`. |
| `T-003` | Manifest entryPoint target missing; only a support file remains | `invalid-missing-index.mdz` (from `src/invalid/missing-index/`) | Consumer rejects with `ERR_ENTRYPOINT_MISSING`: manifest declares `entryPoint: "index.md"` but that file is not present in the archive. It **MUST NOT** silently open `README.md` instead. Recovering to `README.md` (Section 5.5 rules 2–4) passes only with a visible warning. |
| `T-004` | Manifest points to missing file | `invalid-bad-entrypoint.mdz` (from `src/invalid/bad-entrypoint/`) | Consumer rejects with `ERR_ENTRYPOINT_MISSING` (`entryPoint: "missing.md"`). It **MUST NOT** silently open `index.md` instead. Recovering to `index.md` passes only with a visible warning. |
| `T-005` | CRLF text file handling | `line-endings-crlf.mdz` (from `src/line-endings-crlf/`) | Consumer accepts and reads document. |
| `T-006` | Support files in entry point discovery | `entrypoint-cases.json` (support-file cases) | Consumer sets aside root-level `README`, `AGENTS`, `LICENSE`, `CHANGELOG` and `CONTRIBUTING` files (case-insensitive, `.md`/`.markdown`) when applying rule 3 of Section 5.5, and resolves each case to its `expectedEntryPoint`. |
| `T-007` | Archive without a manifest | `minimal.mdz` (from `src/minimal/`) | Consumer opens the archive; it does not reject or warn as non-conforming because `manifest.json` is missing. |
| `T-008` | Invalid vs. missing `entryPoint` | `entrypoint-cases.json` (cases with `expectedError`) | Consumer reports `ERR_ENTRYPOINT_INVALID` for malformed values (non-string, empty, absolute, traversal, backslash, directory, non-Markdown) and `ERR_ENTRYPOINT_MISSING` for valid paths with no matching entry, including case-only differences; it never silently falls back. |
| `T-009` | Path matching | `path-matching-cases.json` | Consumer matches NFC-normalized paths case-sensitively: NFC and NFD forms of the same path match, and there is no case folding (`ß`/`ss`, Greek final sigma, Turkish dotless `ı`). |
| `T-010` | Locale-independent support-file detection | `LICENSE.md` + `notes.md`, with the process locale set to Turkish (`tr-TR`) | Entry point is `notes.md`: support file names are compared ASCII case-insensitively, not with locale rules (which lowercase `LICENSE` to `lıcense`). |
| `T-011` | Link resolution inside, outside and into archives | `link-resolution-cases.json` | Consumer resolves each link to the expected `kind` and target (Sections 9.3–9.5). Consumers that don't support links outside or into archives run the cases with `outsideLinks` / `intoArchiveLinks` set to `false` and must get `unresolved` — never a different target, and never a `..` clamped at the archive root. Targets outside the trust boundary are `denied` whether or not they exist, and resources the document embeds from outside the archive are `denied` unless enabled (Section 9.6). Entry names like `../escape.md` stay invalid (`path-validation-cases.json`). |
| `T-012` | Manifest validation | `manifest-cases.json` | Consumer rejects unreadable manifests and invalid critical fields (`spec`, `spec.version`, `mode`, `entryPoint`) with the listed error, ignores invalid descriptive fields, reads the last of duplicate members and reports them (Section 6.4). |
| `T-013` | Whole-archive entry names | `entry-set-cases.json` | Consumer rejects NFC duplicates (`ERR_DUPLICATE_PATH`) and a file that is also a directory (`ERR_PATH_CONFLICT`); it never picks one entry or renames one (Sections 5.4, 13.1). |
| `T-014` | Unsupported compression method | `unsupported-compression.mdz` (case `unsupported-compression` in `archive-cases.json`) | `index.md` uses BZIP2 (method 12). Consumer reads methods 0 and 8; for any other method it either rejects the archive with `ERR_ZIP_INVALID` or, if it supports the method, reads the entry correctly. It never shows the entry empty or garbled, or treats it as missing (Section 4). |
| `T-015` | Project mode | `project-mode.mdz` (case `project-mode` in `archive-cases.json`) | A project-capable consumer opens `index.md` and each document on its own, never joined (Sections 5.7.2, 5.7.3). A document-only consumer fails with `ERR_MODE_UNSUPPORTED`, or opens the entry point as a document after a user-visible warning; it never falls back silently (Section 5.7.6). |
| `T-016` | Hostile content | `hostile-content.mdz` with `hostile-content-cases.json` | Rendering the entry point runs no script from the archive (`<script>`, event-handler attributes, inline and file SVG scripts, `javascript:` links), ignores the document's `<base>` element, and makes none of the listed requests to the canary origin; the archive's own image still renders. MUST cases cover Sections 9.3 and 13.2; SHOULD cases cover automatic loading over `http:` (Section 9.2) and automatic redirects (Section 13.2). Rendering consumers only: libraries that don't render skip it. |
| `T-017` | Symbolic link entries | `symlink-entries.mdz` (case `symlink-entries` in `archive-cases.json`) | `shortcut.md`, `linked` and `escape.md` are symbolic links (to `notes.md`, `docs` and a path outside the archive). Consumer opens `index.md`, never follows a link: `shortcut.md` and `escape.md` are skipped or read as files containing the target text, `linked/page.md` is unresolved, and extraction creates no symbolic link and writes nothing outside the destination. It SHOULD report each one (Sections 4, 13.1). |
| `T-018` | ZIP-bomb limits | `limit-forged-size.mdz`, `limit-high-ratio.mdz`, `limit-overlapping-entries.mdz` with `resource-limit-cases.json` | With defaults no looser than the case file's `referenceLimits`, consumer rejects each archive or the hostile entry with a stable code (`ERR_LIMIT_EXCEEDED` or `ERR_ZIP_INVALID`) before decompressing the hostile data: an entry that expands past its declared 1 KiB, a 64 MiB entry at about 1029:1, and 300 entries sharing one stream to declare 4.7 GiB. It never returns more than an entry's declared size, and never hides central directory entries (Sections 4, 13.1). SHOULD in the spec; first-party core libraries treat it as MUST. |

## Producer checks

| ID | Case | Expected Result |
|----|------|-----------------|
| `P-001` | New archive | Archive contains `manifest.json` with `spec.version` and an `entryPoint` that references a Markdown file in the archive; `title` and `mode` are present (recommended). |
| `P-002` | Add a support file to an archive with no manifest (for example `notes.md` + new `AGENTS.md`) | Entry point still resolves to `notes.md`; the producer adds `manifest.json` with `entryPoint: "notes.md"` (recommended). |
| `P-004` | Preserve unknown manifest fields | `round-trip.mdz`: run each flow in `round-trip-expectations.json` twice. After every save, each `preservedManifestValues` pointer still holds a JSON-equal value (top-level and nested unknown fields, every JSON type, profile-like fields) (Section 6.3). |
| `P-005` | Preserve untouched entries, including `AGENTS.md` | Same flows: every `preservedEntries` file not listed in the flow's `changes` or `removes` keeps its path, byte length and SHA-256; files in `removes` must be absent. Covers a root `AGENTS.md`, a nested `docs/AGENTS.md`, a `large/AGENTS.md` over 24 KB, an unknown binary file and a CSV (Section 14.1). |
| `P-003` | Add a second support file to an archive whose only Markdown file is a support file (for example `README.md` + new `AGENTS.md`) | Producer adds `manifest.json` with `entryPoint: "README.md"`, so the entry point stays resolvable; leaving the archive ambiguous is non-conforming. |
| `P-006` | Create vs. modify a manifest-less archive | Creating an archive always writes `manifest.json`. Editing a document in an existing archive that has no manifest and saving it is conforming whether or not a manifest is added (adding one is recommended); either way the entry point still resolves to the same file (Section 14.1). |
| `P-007` | Entry names and ZIP flags | Every entry uses method 0 or 8; non-ASCII names carry the UTF-8 flag (bit 11); no empty or `.` segments, no file that is also a directory, no duplicate members in `manifest.json`; every entry is a regular file or a directory, never a symbolic link (Sections 4, 5.4, 6.4). |
| `P-008` | Modify an archive that contains symbolic links | Open `symlink-entries.mdz`, edit `notes.md` and save. The producer writes no new symbolic link. For the three existing ones it either repairs the archive with the user's agreement (removing them, or storing them as regular files) or keeps them and tells the user; it never drops them silently (Section 14.1). |

## Files

Prebuilt `.mdz` archives, built from the folders in [`src/`](src/) (each folder is the archive-root contents before zipping):

- `minimal.mdz`
- `with-manifest.mdz`
- `invalid-missing-index.mdz`
- `invalid-bad-entrypoint.mdz`
- `line-endings-crlf.mdz`
- `round-trip.mdz` — built from `src/round-trip/`; producer preservation checks are in `round-trip-expectations.json` (tests `P-004`, `P-005`).
- `hostile-content.mdz` — built from `src/hostile-content/`: scripts, event handlers, SVG scripts, a `<base>` element and automatic `http:` loads that a renderer must neutralize. The cases, and how to check them with a local canary server, are in `hostile-content-cases.json` (test `T-016`).
- `symlink-entries.mdz` — three symbolic link entries (to a file, to a directory, and out of the archive) next to regular files; a consumer must not follow any of them (Sections 4, 13.1, test `T-017`).
- `unsupported-compression.mdz` — `index.md` compressed with BZIP2 (method 12): reject with `ERR_ZIP_INVALID` or read it correctly (Section 4, test `T-014`).
- `project-mode.mdz` — built from `src/project-mode/`: a `project` archive with three independent documents (Section 5.7, test `T-015`).
- `limit-forged-size.mdz`, `limit-high-ratio.mdz`, `limit-overlapping-entries.mdz` — ZIP bombs under 80 KB each: a declared size smaller than the data, an extreme compression ratio, and entries that share data to declare a huge total (Section 13.1, test `T-018`).

These are generated by [`tools/build-zip-fixtures.py`](../tools/build-zip-fixtures.py), which reproduces them byte for byte. Expected outcomes are in `archive-cases.json` for the first three and in `resource-limit-cases.json` for the `limit-` archives.

Machine-readable case files:

- `entrypoint-cases.json`
- `path-validation-cases.json` — whether a single entry name satisfies Section 5.4 (leading `/`, `..`, `.` and empty segments, reserved and control characters).
- `entry-set-cases.json` — whole-archive name checks: NFC duplicates (`ERR_DUPLICATE_PATH`) and a file that is also a directory (`ERR_PATH_CONFLICT`) (Section 5.4, test `T-013`).
- `manifest-cases.json` — manifest validation: unreadable manifests, critical fields with wrong types or values, ignored descriptive fields, and duplicate member names (Section 6.4, test `T-012`). Each case gives the raw `manifest.json` text in `manifestJson`.
- `link-resolution-cases.json` — link resolution from documents inside an archive and from host files, against a shared model of a vault containing notes, two archives and a directory named `Folder.mdz` (Sections 9.3–9.5, test `T-011`), including query and fragment splitting, invalid and double percent-encoding, encoded `#`, empty segments, trailing slashes, the trust boundary (`denied`) and embedded resources (`use: "embed"`).
- `path-matching-cases.json` — whether a lookup path matches an archive entry under Section 5.4.1 (NFC-normalized, case-sensitive). Non-ASCII characters are written as JSON `\u` escapes so normalization differences stay visible.
- `archive-cases.json` — expected outcomes for `symlink-entries.mdz`, `unsupported-compression.mdz` and `project-mode.mdz` (tests `T-014`, `T-015`, `T-017`).
- `resource-limit-cases.json` — expected outcomes for the `limit-` archives, and the `referenceLimits` a consumer's defaults must not exceed for them to apply (Section 13.1, test `T-018`).
- `create-filter-cases.json`

In `entrypoint-cases.json`, `expectedEntryPoint: null` means no entry point
may be selected. Cases that also set `expectedError` name the error the
consumer should report (for example `ERR_ENTRYPOINT_MISSING`, where the
consumer must not silently fall back to another file).

`manifest` is the manifest as a JSON object, or `null` for none. A case whose
manifest isn't a valid manifest shape (for example `"entryPoint": 42`) sets
`manifest` to `null` and gives the exact `manifest.json` text in
`manifestJson` instead; harnesses write that text verbatim. This keeps the
file loadable by implementations that deserialize `manifest` into a typed
model.

These JSON fixtures are intended to be consumed by multiple implementations
(for example, C# and TypeScript) so both can assert the same behavior from a
shared set of cases. They are non-normative ([Section 14.3](../SPEC.md#143-conformance-fixtures)):
when a fixture and `SPEC.md` disagree, `SPEC.md` governs and the fixture is a
defect to report.

## Using these fixtures in an implementation

Copy them from a **released spec tag** with the sync tool, rather than by hand
or from a working copy of this repository:

```sh
# from the implementation repo, with mdzip-spec checked out alongside it
node ../mdzip-spec/tools/sync-fixtures.mjs tests/fixtures --ref v1.2.1
```

This writes the fixtures and a `SPEC-FIXTURES.json` marker recording the tag,
its commit and each file's SHA-256. Commit both. To catch a hand-edited or
stale copy, run the check in CI (or reimplement it in the test suite: compare
each file's SHA-256 with the marker):

```sh
node ../mdzip-spec/tools/sync-fixtures.mjs tests/fixtures --check
```

- Pin to a tag, not a branch. Fixtures on a draft branch describe rules an
  implementation may not support yet.
- Put implementation-specific cases in separate files next to the copy (for
  example `local-entrypoint-cases.json`); the sync tool never touches files
  that aren't spec fixtures. If a local case encodes behavior every
  implementation should share, propose it for this folder.
- Don't read fixtures straight from a sibling `mdzip-spec` checkout at test
  time: the result then depends on which branch happens to be checked out.
