# examples

Sample `.mdz` package structures for implementers.

## Included Starter Cases

- `minimal/` - smallest valid archive-root contents (only `index.md`).
- `with-manifest/` - valid package with optional `manifest.json` and nested assets.
- `invalid/missing-index/` - invalid case: required `index.md` absent.
- `invalid/bad-entrypoint/` - invalid case: manifest `entryPoint` does not exist.
- `line-endings-crlf/` - valid compatibility case for consumer CRLF handling.

## Usage

- Treat each directory as archive-root content, zip it, then rename to `.mdz`.
- Expected outcomes are documented in [tests/README.md](../tests/README.md).
- Prebuilt fixture archives are available in [`examples/fixtures/`](fixtures/).
- A reusable human-facing package `README.md` template is available at [`examples/templates/README.sample.md`](templates/README.sample.md).
