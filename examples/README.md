# examples

Sample `.mdz` package structures for implementers.

## Included Starter Cases

- `minimal/` - smallest valid archive-root contents (only `index.md`).
- `with-manifest/` - valid package with optional `manifest.json` and nested assets.
- `invalid/missing-index/` - invalid case: manifest declares `entryPoint: "index.md"` but the file is absent (`ERR_ENTRYPOINT_MISSING`).
- `invalid/bad-entrypoint/` - invalid case: manifest `entryPoint` does not exist.
- `line-endings-crlf/` - valid compatibility case for consumer CRLF handling.
- `round-trip/` - producer preservation case: a manifest with unknown fields of every JSON type (top level, nested in known objects, profile-like), `AGENTS.md` at the root, nested and over 24 KB, plus an unknown binary file and a CSV. Prebuilt as `fixtures/round-trip.mdz`; checks in `fixtures/round-trip-expectations.json` (tests `P-004`, `P-005`). Its files are stored with `-text` in `.gitattributes` so checksums don't change on checkout.

## Usage

- Treat each directory as archive-root content, zip it, then rename to `.mdz`.
- Expected outcomes are documented in [tests/README.md](../tests/README.md).
- Prebuilt fixture archives are available in [`examples/fixtures/`](fixtures/).
- A reusable human-facing package `README.md` template is available at [`examples/templates/README.sample.md`](templates/README.sample.md), and an agent-facing `AGENTS.md` template at [`examples/templates/AGENTS.sample.md`](templates/AGENTS.sample.md).
