# tests

Conformance test catalog for `.mdz` producers and consumers.

## Test Matrix

| ID | Case | Input | Expected Result |
|----|------|-------|-----------------|
| `T-001` | Minimal valid package | `examples/minimal/` | Consumer opens `index.md` as primary document. |
| `T-002` | Valid package with manifest | `examples/with-manifest/` | Consumer uses `manifest.json.entryPoint`. |
| `T-003` | Missing required root `index.md` | `examples/invalid/missing-index/` | Consumer rejects as non-conforming. |
| `T-004` | Manifest points to missing file | `examples/invalid/bad-entrypoint/` | Consumer rejects as non-conforming. |
| `T-005` | CRLF text file handling | `examples/line-endings-crlf/` | Consumer accepts and reads document. |

## Notes

- Each test input directory represents archive-root contents before zipping.
- A harness MAY zip each directory as `*.mdz` and validate the expected outcome.
- Add producer-side checks separately (for example, path normalization and traversal rejection).
- Generated fixture archives are stored in [`examples/fixtures/`](../examples/fixtures/):
  - `minimal.mdz`
  - `with-manifest.mdz`
  - `invalid-missing-index.mdz`
  - `invalid-bad-entrypoint.mdz`
  - `line-endings-crlf.mdz`
