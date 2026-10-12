# Fixture Archives

Prebuilt `.mdz` archives generated from the source directories in [`../`](../README.md).

Files:

- `minimal.mdz`
- `with-manifest.mdz`
- `invalid-missing-index.mdz`
- `invalid-bad-entrypoint.mdz`
- `line-endings-crlf.mdz`
- `round-trip.mdz` — built from `../round-trip/`; producer preservation checks are in `round-trip-expectations.json` (tests `P-004`, `P-005`).

Machine-readable behavior fixtures:

- `entrypoint-cases.json`
- `path-validation-cases.json` — whether a single entry name satisfies Section 5.4 (leading `/`, `..`, `.` and empty segments, reserved and control characters).
- `entry-set-cases.json` — whole-archive name checks: NFC duplicates (`ERR_DUPLICATE_PATH`) and a file that is also a directory (`ERR_PATH_CONFLICT`) (Section 5.4, test `T-013`).
- `manifest-cases.json` — manifest validation: unreadable manifests, critical fields with wrong types or values, ignored descriptive fields, and duplicate member names (Section 6.4, test `T-012`). Each case gives the raw `manifest.json` text in `manifestJson`.
- `link-resolution-cases.json` — link resolution from documents inside an archive and from host files, against a shared model of a vault containing notes, two archives and a directory named `Folder.mdz` (Sections 9.3–9.5, test `T-011`), including query and fragment splitting, invalid and double percent-encoding, encoded `#`, empty segments and trailing slashes.
- `path-matching-cases.json` — whether a lookup path matches an archive entry under Section 5.4.1 (NFC-normalized, case-sensitive). Non-ASCII characters are written as JSON `\u` escapes so normalization differences stay visible.
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
shared source of truth.

## Using these fixtures in an implementation

Copy them from a **released spec tag** with the sync tool, rather than by hand
or from a working copy of this repository:

```sh
# from the implementation repo, with mdzip-spec checked out alongside it
node ../mdzip-spec/tools/sync-fixtures.mjs tests/fixtures --ref v1.1.0
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
