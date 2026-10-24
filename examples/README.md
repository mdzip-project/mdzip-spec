# Examples and guidance

Explanatory, **non-normative** material for people producing or reading `.mdz`
files. The requirements are in [`SPEC.md`](../SPEC.md); the executable
conformance cases are in [`fixtures/`](../fixtures/README.md). When anything
here disagrees with `SPEC.md`, `SPEC.md` governs.

## Templates

- [`templates/README.sample.md`](templates/README.sample.md) - a reusable human-facing package `README.md` (Section 5.6).
- [`templates/AGENTS.sample.md`](templates/AGENTS.sample.md) - a reusable agent-facing `AGENTS.md` for tools without native `.mdz` support (Section 5.8).

## Sample packages

Each fixture archive is built from a plain folder you can browse, in
[`fixtures/src/`](../fixtures/src/). Good starting points:

- [`minimal/`](../fixtures/src/minimal/) - the smallest valid archive: only `index.md`, no manifest.
- [`with-manifest/`](../fixtures/src/with-manifest/) - a `manifest.json` with an `entryPoint`, and nested assets.
- [`project-mode/`](../fixtures/src/project-mode/) - a `project` archive with three independent documents.
- [`round-trip/`](../fixtures/src/round-trip/) - unknown manifest fields and an `AGENTS.md` a producer must preserve.

To try one by hand, zip the folder's contents (not the folder itself) and
rename the result to `.mdz`. The prebuilt archives are next to the cases in
[`fixtures/`](../fixtures/README.md#files).

## Design rationale

[`rationale.md`](rationale.md) explains why the format is the way it is: why
ZIP, why `index.md`, why a JSON manifest, why no mandated Markdown dialect,
modes, and more.
