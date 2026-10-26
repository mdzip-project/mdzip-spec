# Contributing

Thanks for helping improve the MDZip (`.mdz`) specification.

## Scope

- Normative requirements belong in [SPEC.md](SPEC.md).
- Conformance tests and fixtures belong in [`fixtures/`](fixtures/README.md) (fixture source folders in `fixtures/src/`).
- Non-normative templates, guidance and rationale belong in [`examples/`](examples/README.md) (rationale in [`examples/rationale.md`](examples/rationale.md)).

## Change Process

1. Open an issue describing the change and rationale.
2. Submit a pull request with focused edits.
3. Update related fixtures and examples when normative behavior changes.
4. Add an entry in [CHANGELOG.md](CHANGELOG.md).

## Editorial Rules

- Use RFC 2119 terms consistently (`MUST`, `SHOULD`, `MAY`).
- Keep requirements implementation-neutral.
- Avoid feature creep; prefer minimal, interoperable behavior.
- Keep examples deterministic and cross-platform.

## Versioning Policy

- Spec versions follow Semantic Versioning.
- Breaking format changes require a major version bump.
- Backward-compatible additions/clarifications require a minor bump.
- Editorial fixes require a patch bump.
- Changes that leave conformance unchanged also get a patch release: new or
  corrected fixtures, tools, examples and non-normative sections. Implementations
  pin fixtures to a tag, so they need a release to pick these up. A patch
  release doesn't change what conforming archives or implementations look like;
  producers may keep writing the earlier `spec.version` of the same minor.
